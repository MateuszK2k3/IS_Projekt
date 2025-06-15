#!/usr/bin/env bash
set -e

echo "==> Czekam na bazę danych..."

# Czeka aż baza zacznie przyjmować połączenia (host i port z ENV)
until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  echo "czekam na $POSTGRES_HOST:$POSTGRES_PORT..."
  sleep 1
done

echo "==> Baza działa, wykonuję migracje..."
export FLASK_APP=wsgi.py
flask db upgrade

echo "==> Startuję aplikację"
exec gunicorn -b 0.0.0.0:8000 wsgi:app
