#!/usr/bin/env python3
# hub.py

from flask import Flask, render_template, url_for, request
# The publisher and hub are combined in the same process because it's easier.
# There's no need to do so, though.
from flask_websub.publisher import publisher, init_publisher
from flask_websub.hub import Hub, SQLite3HubStorage
from flask_websub.subscriber import Subscriber, SQLite3TempSubscriberStorage, \
                                    SQLite3SubscriberStorage, discover

from celery import Celery
from urllib.request import urlopen
from urllib.parse import quote, unquote

# app & celery
app = Flask(__name__)
app.config['SERVER_NAME'] = 'hub.websub.local'
celery = Celery('hub', broker='redis://localhost:6379')

# initialise publisher
init_publisher(app)

# initialise hub
#
# PUBLISH_SUPPORTED is not recommended in production, as it just accepts any
# link without validation, but it's but nice for testing.
app.config['PUBLISH_SUPPORTED'] = True
# we could also have passed in just PUBLISH_SUPPORTED, but this is probably a
# nice pattern for your app:
hub = Hub(SQLite3HubStorage('hub.sqlite3'), celery, **app.config)
app.register_blueprint(hub.build_blueprint(url_prefix='/hub'))

subscriber = Subscriber(SQLite3SubscriberStorage('hubsub.sqlite3'),
                        SQLite3TempSubscriberStorage('hubsub.sqlite3'))
app.register_blueprint(subscriber.build_blueprint(url_prefix='/callbacks'))

#Metadata storage
mdstor = {}

@subscriber.add_success_handler
def on_success(topic_url, callback_id, mode):
    print("SUCCESS!", topic_url, callback_id, mode)
    global mdstor
    #topic_url = unquote(topic_url)
    mdsrc = urlopen(topic_url).read().decode('utf-8')
    mdstor[topic_url] = mdsrc


@subscriber.add_error_handler
def on_error(topic_url, callback_id, msg):
    print("ERROR!", topic_url, callback_id, msg)


@subscriber.add_listener
def on_topic_change(topic_url, callback_id, body):
    print('TOPIC CHANGED!', topic_url, callback_id, body)
    global mdstor
    topic = "http://hub.websub.local/md?id={}".format(quote(topic_url, safe=':'))
    print("update: {}".format(topic))
    hub.send_change_notification.delay(topic)
    topic_url = unquote(topic_url)
    mdsrc = urlopen(topic_url).read().decode('utf-8')
    mdstor[topic_url] = mdsrc


def validate_topic_existence(callback_url, topic_url, *args):
    with app.app_context():
        if (topic_url.startswith('http://idp.websub.local/') or
            topic_url.startswith('http://mdq.websub.local/')):
            return  # pass validation
        if topic_url != url_for('topic', _external=True):
            return "Topic not allowed"


hub.register_validator(validate_topic_existence)
hub.schedule_cleanup()  # cleanup expired subscriptions once a day, by default


@app.before_first_request
def cleanup():
    # or just cleanup manually at some point
    hub.cleanup_expired_subscriptions.delay()

# Pub endpoint
@app.route('/')
@publisher()
def topic():
    msg = "Hub home"
    return render_template('hub.html', message=msg)

@app.route('/md')
@publisher()
def md():
    global mdstor
    id = request.args.get('id', None)
    mdsrc = mdstor.get(id, None)
    md = "[hub]{}[hub]".format(mdsrc)
    return md

# The test metadata on pub
published_url = 'http://pub.websub.local/entities/https:%2F%2Fidp.mrvanes.com%2Fsaml%2Fsaml2%2Fidp%2Fmetadata.php'

# Hub endpoint
@app.route('/update/<id>')
@publisher()
def update(id):
    print("update: {}".format(id))
    hub.send_change_notification.delay(id)
    return "Notification send!"

# Subscriber endpoints
@app.route('/subscribe')
@publisher()
def subscribe_route():
    id = subscriber.subscribe(**discover(published_url))
    return 'Subscribed. ' + url_for('renew_route', id=id, _external=True)


@app.route('/renew/<id>')
@publisher()
def renew_route(id):
    new_id = subscriber.renew(id)
    return 'Renewed: ' + url_for('unsubscribe_route', id=new_id,
                                 _external=True)


@app.route('/unsubscribe/<id>')
@publisher()
def unsubscribe_route(id):
    subscriber.unsubscribe(id)
    return 'Unsubscribed: ' + url_for('cleanup_and_renew_all', _external=True)


@app.route('/cleanup_and_renew_all')
@publisher()
def cleanup_and_renew_all():
    subscriber.cleanup()
    # 100 days, to make sure every single subscription is renewed
    subscriber.renew_close_to_expiration(24 * 60 * 60 * 100)
    return 'Done!'



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
