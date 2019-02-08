#!/usr/bin/sh

python manage.py migrate --no-input

/usr/local/bin/gunicorn -b 0.0.0.0:8000 --reload --access-logfile - journal.wsgi:application
