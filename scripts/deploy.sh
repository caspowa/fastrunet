#!/bin/bash -ex
virtualenv -p python3.3 env
env/bin/pip install --timeout=120 -r requirements.txt

if [ ! -f /tmp/fastrunet.pid ] && [ kill -0 `cat /tmp/uwsgi.fastrunet.pid` ]; then
    env/bin/uwsgi --stop /tmp/uwsgi.fastrunet.pid
fi

env/bin/uwsgi -x uwsgi.xml
