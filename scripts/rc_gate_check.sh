#!/usr/bin/env bash
set -eo pipefail

echo "========================================================================"
echo "🚀 INITIATING RELEASE CANDIDATE GATE (MILESTONE M3 AUDIT)"
echo "========================================================================"

# 1. Ruff Linter & Formatter checks
echo "--> [1/5] Running Ruff Linter & Formatter checks..."
uv run ruff check .
uv run ruff format --check .

# 2. Django database migrations integrity
echo "--> [2/5] Checking Django database migrations integrity..."
uv run python manage.py makemigrations --check --dry-run

# 3. Production deployment security hardening
echo "--> [3/5] Verifying Django deployment security hardening..."
DJANGO_SETTINGS_MODULE=config.settings.production uv run python manage.py check --deploy

# 4. Unit, Functional, Integration & Security Tests with Coverage
echo "--> [4/5] Running Unit, Integration & Security Tests with Coverage..."
uv run pytest tests/unit/ tests/functional/ tests/integration/ --cov=apps --cov=integrations --cov-report=term-missing --cov-fail-under=80

# 5. Playwright E2E Browser Test Suite
echo "--> [5/5] Running Playwright E2E Browser Test Suite..."
uv run pytest tests/e2e/ --no-cov

echo "========================================================================"
echo "✅ MILESTONE M3 GATE PASSED: ALL CHECKS & TESTS GREEN"
echo "========================================================================"
