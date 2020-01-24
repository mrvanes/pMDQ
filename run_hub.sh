#!/bin/sh
cd /opt/websub
/opt/websub/bin/celery -A hub.celery worker -l info &
/opt/websub/bin/python /opt/websub/hub.py

