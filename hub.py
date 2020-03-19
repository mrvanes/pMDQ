#!/usr/bin/env python3
# hub.py

from flask import Flask, render_template, url_for, request
# The publisher and hub are combined in the same process because it's easier.
# There's no need to do so, though.
from flask_websub.hub import Hub, SQLite3HubStorage

from celery import Celery
from urllib.request import urlopen
from urllib.parse import quote, unquote

# app & celery
app = Flask(__name__)
app.config['SERVER_NAME'] = 'hub.websub.local'
app.config['REQUEST_TIMEOUT'] = 3
app.config['BACKOFF_BASE'] = 1.0

celery = Celery('hub', broker='redis://localhost:6379')

# initialise hub
#
# PUBLISH_SUPPORTED is not recommended in production, as it just accepts any
# link without validation, but it's but nice for testing.
app.config['PUBLISH_SUPPORTED'] = False
# we could also have passed in just PUBLISH_SUPPORTED, but this is probably a
# nice pattern for your app:
hub = Hub(SQLite3HubStorage('hub.sqlite3'), celery, **app.config)
app.register_blueprint(hub.build_blueprint(url_prefix='/hub'))

def validate_topic_existence(callback_url, topic_url, *args):
    #print("validate: {}".format(topic_url))
    with app.app_context():
        if (topic_url.startswith('http://feda.websub.local/') or
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

# Root endpoint
@app.route('/')
def topic():
    msg = "Hub home"
    return render_template('hub.html', message=msg)

# Hub endpoint
@app.route('/update', methods=['POST'])
def update():
    topic = request.form.get('topic', None)
    print("update: {}".format(topic))
    hub.send_change_notification.delay(topic)
    return "Notification sent!\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
