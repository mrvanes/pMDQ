#!/usr/bin/env python3
# subscriber.py

from flask import Flask, url_for, render_template
from flask_websub.subscriber import Subscriber, SQLite3TempSubscriberStorage, \
                                    SQLite3SubscriberStorage, discover

from urllib.request import urlopen
from urllib.parse import unquote

app = Flask(__name__)
app.config['SERVER_NAME'] = 'sub.websub.local'

subscriber = Subscriber(SQLite3SubscriberStorage('subscriber.sqlite3'),
                        SQLite3TempSubscriberStorage('subscriber.sqlite3'))
app.register_blueprint(subscriber.build_blueprint(url_prefix='/callbacks'))

#Metadata store
mdstor = {}

@subscriber.add_success_handler
def on_success(topic_url, callback_id, mode):
    print("SUCCESS!", topic_url, callback_id, mode)
    global mdstor
    topic_url = unquote(topic_url)
    mdsrc = urlopen(topic_url).read().decode('utf-8')
    mdstor[topic_url] = mdsrc    

@subscriber.add_error_handler
def on_error(topic_url, callback_id, msg):
    print("ERROR!", topic_url, callback_id, msg)


@subscriber.add_listener
def on_topic_change(topic_url, callback_id, body):
    print('TOPIC CHANGED!', topic_url, callback_id, body)
    global mdstor
    topic_url = unquote(topic_url)
    mdsrc = urlopen(topic_url).read().decode('utf-8')
    mdstor[topic_url] = mdsrc    


published_url = 'http://hub.websub.local/md?id=http://pub.websub.local/md'

@app.route('/')
def topic():
    global mdstor
    msg = "Subscriber home"
    md = ""
    for mdid,v in mdstor.items():
        md += "{}<br>\n{}<br>\n".format(mdid, v)
    return render_template('subscriber.html', message=msg, metadata=md)

@app.route('/subscribe')
def subscribe_route():
    id = subscriber.subscribe(**discover(published_url))
    return 'Subscribed. ' + url_for('renew_route', id=id, _external=True)


@app.route('/renew/<id>')
def renew_route(id):
    new_id = subscriber.renew(id)
    return 'Renewed: ' + url_for('unsubscribe_route', id=new_id,
                                 _external=True)


@app.route('/unsubscribe/<id>')
def unsubscribe_route(id):
    subscriber.unsubscribe(id)
    return 'Unsubscribed: ' + url_for('cleanup_and_renew_all', _external=True)


@app.route('/cleanup_and_renew_all')
def cleanup_and_renew_all():
    subscriber.cleanup()
    # 100 days, to make sure every single subscription is renewed
    subscriber.renew_close_to_expiration(24 * 60 * 60 * 100)
    return 'Done!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
