#!/bin/bash -ex
virtualenv -p python2.7 env
env/bin/pip install --timeout=120 -r requirements.txt

if [ ! -f /tmp/bportal.pid ] && [ kill -0 `cat /tmp/uwsgi.bportal.pid` ]; then
    env/bin/uwsgi --stop /tmp/uwsgi.bportal.pid
fi

env/bin/python scripts/fill_secret_keys.py src/secret_keys.py

env/bin/uwsgi -x uwsgi.xml

env/bin/python src/crawler.py stop
env/bin/python src/crawler.py start
