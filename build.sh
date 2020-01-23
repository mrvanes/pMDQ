#!/bin/sh
if [ ! -f websub_key ]; then
  ssh-keygen -f websub_key -N ''
fi
docker-compose build
docker-compose up --no-start
