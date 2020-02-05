#!/bin/sh
cd /opt/websub
redis-cli flushall
rm hub.sqlite3
rm hubsub.sqlite3
/opt/websub/bin/celery -A hub.celery worker -l info &
/opt/websub/bin/python /opt/websub/hub.py

