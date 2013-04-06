#!/bin/bash -ex
virtualenv env
env/bin/pip install --timeout=120 -r requirements.txt
env/bin/uwsgi --stop /tmp/uwsgi.bportal.pid
env/bin/python scripts/fill_secret_keys.py src/secret_keys.py
env/bin/uwsgi -x uwsgi.xml
env/bin/python src/crawler.py stop
env/bin/python src/crawler.py start
