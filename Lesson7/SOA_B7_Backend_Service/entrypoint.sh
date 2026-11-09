#!/bin/sh
set -eu

flask --app 'product_api.factory:create_app' db upgrade
exec gunicorn -c gunicorn.conf.py wsgi:app
