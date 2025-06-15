#!/usr/bin/env bash
set -e

# 1) Czekaj aż baza odpowie
echo "==> Czekam na bazę danych..."
until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" ; do
  sleep 1
done

# 2) Migracje Alembic
echo "==> Wykonuję migracje..."
export FLASK_APP=wsgi.py
flask db upgrade

# 3) Start aplikacji
echo "==> Startuję aplikację"
exec gunicorn -b 0.0.0.0:8000 wsgi:app
