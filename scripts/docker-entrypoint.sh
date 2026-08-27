#!/usr/bin/env bash
set -eo pipefail

# Execute production pre-flight checks and apply pending database migrations
python scripts/prod_preflight_check.py

echo "==> Starting Gunicorn Application Server..."
exec "$@"
