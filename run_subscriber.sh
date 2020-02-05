#!/bin/sh
cd /opt/websub
rm subscriber.sqlite3
/opt/websub/bin/python /opt/websub/subscriber.py
