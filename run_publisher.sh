#!/bin/sh
cd /opt/websub
/opt/websub/bin/celery -A publisher.celery worker -l info &
/opt/websub/bin/python /opt/websub/publisher.py
