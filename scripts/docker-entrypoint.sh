#!/usr/bin/env bash
set -eo pipefail

# Execute production pre-flight checks and apply pending database migrations
python scripts/prod_preflight_check.py

PORT="${PORT:-8000}"

echo "==> Starting Gunicorn Application Server on port ${PORT}..."
if [ "$#" -eq 0 ] || [ "$1" = "gunicorn" ]; then
    exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT}" --workers 3 --timeout 60 --access-logfile - --error-logfile -
else
    eval "exec $@"
fi
