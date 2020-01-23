#!/bin/sh
celery -A hub.celery worker -l info

