#!/bin/sh
cd /opt/websub
if [ ! -d "/opt/websub/lib" ]; then
  virtualenv --python=python3 .
  /opt/websub/bin/pip install -e .
  /opt/websub/bin/pip install celery
  /opt/websub/bin/pip install redis
fi
redis-cli flushall
rm hub.sqlite3
rm hubsub.sqlite3
/opt/websub/bin/celery -A hub.celery worker -l info &
/opt/websub/bin/python /opt/websub/hub.py

