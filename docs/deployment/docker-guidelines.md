# Production Docker Image Guidelines (Phase 12 - T-061)

## Architecture Overview
The portfolio container image is built using a multi-stage Dockerfile architecture based on Python 3.14-slim and the fast `uv` package manager.

## Key Security & Optimization Features
1. **Multi-stage Build**: Separates build tooling and package caches from runtime artifacts to ensure minimal image size.
2. **Non-Root Execution**: Runs under a dedicated unprivileged user (`appuser:appgroup`, UID/GID 1001) for container security.
3. **Deterministic Dependencies**: Synchronizes production packages using `uv sync --frozen --no-dev`.
4. **Built-in Static File Optimization**: Pre-compiles static files via `python manage.py collectstatic --noinput` with WhiteNoise hashing and compression.
5. **Production WSGI Server**: Uses Gunicorn configured with 3 worker processes, synchronous timeouts, and stdout/stderr stream logging.

## Local Build & Verification Commands

```bash
# Build the Docker image
docker build -t portfolio-app:rc .

# Verify non-root user execution
docker run --rm portfolio-app:rc whoami
# Expected output: appuser

# Run container locally with environment variables
docker run --rm -d -p 8000:8000 \
  -e SECRET_KEY="runtime-secret-key-12345" \
  -e ALLOWED_HOSTS="localhost,127.0.0.1" \
  -e DATABASE_URL="sqlite:////tmp/test.db" \
  --name portfolio-test-container portfolio-app:rc

# Verify container HTTP response
curl -I http://localhost:8000/en/

# Stop and cleanup container
docker stop portfolio-test-container
```
