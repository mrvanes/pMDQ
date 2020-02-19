#!/bin/sh
git clone https://github.com/mrvanes/pyFF.git -b websub
git clone https://github.com/mrvanes/pMDQ.git websub
docker-compose build --force-rm
docker-compose up --no-start
