#!/bin/bash

while ! nc -z db 5432; do
  sleep 1
done

export FLASK_APP=wsgi.py
export PYTHONPATH=/app

python -c "
from app import db
from wsgi import app

with app.app_context():
    db.create_all()
"

exec flask run -h 0.0.0.0
