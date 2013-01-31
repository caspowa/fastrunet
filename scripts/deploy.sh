virtualenv env
env/bin/pip install --timeout=120 -r requirements.txt
env/bin/uwsgi --stop /tmp/uwsgi.bportal.pid
env/bin/python scripts/fill_secret_keys.py src/secret_keys.py /var/bportal.keys
env/bin/uwsgi -x uwsgi.xml