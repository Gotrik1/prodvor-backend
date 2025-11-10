#!/bin/sh
# backend/entrypoint.sh

set -e

# Требуется для flask cli с фабрикой приложения
export FLASK_APP="app:create_app()"
export FLASK_ENV=production

echo "Applying database migrations..."
flask db upgrade

echo "Starting Gunicorn..."
exec gunicorn "app:create_app()" \
  -k gthread \
  -w 2 \
  --threads 8 \
  -t 30 \
  --graceful-timeout 20 \
  --max-requests 2000 \
  --max-requests-jitter 200 \
  --bind "0.0.0.0:5000"