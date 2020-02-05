#!/bin/sh
cd /opt/websub
redis-cli flushall
rm publisher.sqlite3
/opt/websub/bin/celery -A publisher.celery worker -l info &
/opt/websub/bin/python /opt/websub/publisher.py
