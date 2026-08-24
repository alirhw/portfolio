import logging

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def healthcheck_view(request):
    """
    Liveness & Readiness probe.
    Checks database connection and cache connectivity without exposing internal metadata.
    """
    status_report = {
        "status": "healthy",
        "checks": {
            "database": "unknown",
            "cache": "unknown",
        },
    }
    http_status = 200

    # 1. Database connection check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row and row[0] == 1:
                status_report["checks"]["database"] = "ok"
            else:
                status_report["checks"]["database"] = "error"
                status_report["status"] = "unhealthy"
                http_status = 503
    except Exception as exc:
        logger.error("Healthcheck Database failure: %s", exc, exc_info=True)
        status_report["checks"]["database"] = "unavailable"
        status_report["status"] = "unhealthy"
        http_status = 503

    # 2. Cache read/write ping
    try:
        cache_key = "healthcheck_ping"
        cache.set(cache_key, "pong", timeout=10)
        cached_val = cache.get(cache_key)
        if cached_val == "pong":
            status_report["checks"]["cache"] = "ok"
        else:
            status_report["checks"]["cache"] = "error"
            status_report["status"] = "unhealthy"
            http_status = 503
    except Exception as exc:
        logger.warning("Healthcheck Cache failure: %s", exc)
        status_report["checks"]["cache"] = "unavailable"
        status_report["status"] = "unhealthy"
        http_status = 503

    return JsonResponse(status_report, status=http_status)


def sentry_debug_trigger_view(request):
    """
    Controlled 500 trigger view to verify Sentry exception capture in test environments.
    """
    logger.error("Triggering intentional 500 error for Sentry verification.")
    raise ZeroDivisionError("Sentry test division by zero.")
