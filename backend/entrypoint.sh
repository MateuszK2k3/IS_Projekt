#!/bin/bash

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Database is up!"

export FLASK_APP=wsgi.py
export PYTHONPATH=/app

# Inicjalizacja bazy danych
python -c "
from app import db
from wsgi import app

with app.app_context():
    db.create_all()
"

# Uruchom aplikację
exec flask run -h 0.0.0.0
