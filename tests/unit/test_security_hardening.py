import importlib

import pytest
from django.core.management import call_command
from django.test import override_settings


def test_production_settings_flags():
    """
    Verify production.py security flags comply with T-054 standard.
    """
    prod_settings = importlib.import_module("config.settings.production")

    assert prod_settings.DEBUG is False
    assert prod_settings.SECURE_SSL_REDIRECT is True
    assert prod_settings.SESSION_COOKIE_SECURE is True
    assert prod_settings.CSRF_COOKIE_SECURE is True
    assert prod_settings.SECURE_HSTS_SECONDS == 31536000
    assert prod_settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert prod_settings.SECURE_HSTS_PRELOAD is True
    assert prod_settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert prod_settings.SECURE_BROWSER_XSS_FILTER is True
    assert prod_settings.X_FRAME_OPTIONS == "DENY"


@pytest.mark.django_db
@override_settings(
    SECURE_CONTENT_TYPE_NOSNIFF=True,
    SECURE_BROWSER_XSS_FILTER=True,
    X_FRAME_OPTIONS="DENY",
    SECURE_REFERRER_POLICY="strict-origin-when-cross-origin",
)
def test_response_security_headers_present(client):
    """
    Verify security headers are present in HTTP response.
    """
    response = client.get("/en/")
    assert response.status_code == 200

    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "camera=()" in response.headers.get("Permissions-Policy", "")
    assert response.headers.get("Cross-Origin-Opener-Policy") == "same-origin"


def test_django_deploy_check_clean(monkeypatch):
    """
    Execute Django deploy health check against production configuration.
    """
    monkeypatch.delenv("DJANGO_ALLOW_ASYNC_UNSAFE", raising=False)
    prod_settings = importlib.import_module("config.settings.production")
    prod_dict = {
        k: getattr(prod_settings, k)
        for k in dir(prod_settings)
        if k.isupper() and k not in ("DATABASES",)
    }
    with override_settings(**prod_dict):
        call_command("check", deploy=True)
