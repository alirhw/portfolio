#!/usr/bin/env bash
set -eo pipefail

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Starting application server..."
exec "$@"
