from unittest.mock import patch

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_healthcheck_endpoint_returns_200_when_healthy(client):
    """
    Verify healthy response and standard JSON structure of healthz endpoint.
    """
    url = reverse("healthcheck")
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["cache"] == "ok"


@pytest.mark.django_db
def test_healthcheck_returns_503_on_database_disconnection(client):
    """
    Verify 503 response code when database connection fails.
    """
    url = reverse("healthcheck")

    with patch("django.db.connection.cursor", side_effect=Exception("Database down")):
        response = client.get(url)

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["checks"]["database"] == "unavailable"


@pytest.mark.django_db
def test_healthcheck_returns_503_on_cache_failure(client):
    """
    Verify 503 response code when cache operations fail.
    """
    url = reverse("healthcheck")

    with patch("django.core.cache.cache.set", side_effect=Exception("Redis connection refused")):
        response = client.get(url)

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["checks"]["cache"] == "unavailable"


def test_sentry_debug_trigger_view_raises_500(client):
    """
    Verify intentional 500 error view triggers exception for Sentry validation.
    """
    with pytest.raises(ZeroDivisionError):
        client.get("/_debug/sentry-trigger/")
