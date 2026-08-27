#!/usr/bin/env bash
set -eo pipefail

IMAGE_TAG="${1:-portfolio-app:ci-test}"

echo "========================================================================"
echo "🐳 EXECUTING DOCKER SMOKE TEST: ${IMAGE_TAG}"
echo "========================================================================"

# 1. Verify Non-root user
echo "--> [1/3] Verifying Non-root user..."
RUNNER_USER=$(docker run --rm --entrypoint whoami "${IMAGE_TAG}")
if [ "${RUNNER_USER}" != "appuser" ]; then
    echo "❌ Security failure: Container executed as '${RUNNER_USER}' instead of 'appuser'"
    exit 1
fi
echo "✔ Running securely as user: ${RUNNER_USER}"

# 2. Start temporary container instance in background
echo "--> [2/3] Starting temporary container instance..."
CONTAINER_ID=$(docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY="ci-smoke-test-secret-key" \
  -e ALLOWED_HOSTS="localhost,127.0.0.1" \
  -e DATABASE_URL="sqlite:////tmp/smoke_test.db" \
  -e SECURE_SSL_REDIRECT="False" \
  "${IMAGE_TAG}")

# Cleanup function on script exit
cleanup() {
    echo "--> Cleaning up smoke test container..."
    docker stop "${CONTAINER_ID}" > /dev/null 2>&1 || true
    docker rm "${CONTAINER_ID}" > /dev/null 2>&1 || true
}
trap cleanup EXIT

# 3. Poll /healthz/ endpoint with retry mechanism
echo "--> [3/3] Polling /healthz/ endpoint..."
MAX_RETRIES=15
COUNT=0
HEALTH_STATUS=1

until [ $COUNT -ge $MAX_RETRIES ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "X-Forwarded-Proto: https" http://localhost:8000/healthz/ || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        HEALTH_STATUS=0
        break
    fi
    COUNT=$((COUNT+1))
    sleep 1
done

if [ $HEALTH_STATUS -ne 0 ]; then
    echo "❌ Smoke test failed: /healthz/ did not return 200 OK (Last HTTP code: ${HTTP_CODE})"
    docker logs "${CONTAINER_ID}"
    exit 1
fi

echo "========================================================================"
echo "✅ DOCKER SMOKE TEST PASSED: CONTAINER IS PRODUCTION-READY"
echo "========================================================================"
