#!/bin/sh
celery -A publisher.celery worker -l info
