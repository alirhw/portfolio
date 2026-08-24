import pytest
from django.test import override_settings

from apps.core.csp import build_csp_header


def test_build_csp_header_format():
    header = build_csp_header()

    # Check key directives
    assert "default-src 'self'" in header
    assert "object-src 'none'" in header
    assert "frame-ancestors 'none'" in header
    assert "base-uri 'self'" in header

    # Verify Cloudflare Turnstile challenge domain presence in script and frame
    assert "https://challenges.cloudflare.com" in header


def test_script_src_does_not_contain_unsafe_eval():
    header = build_csp_header()
    # Ensure unsafe-eval is blocked
    assert "'unsafe-eval'" not in header


@pytest.mark.django_db
@override_settings(CSP_ENABLED=True)
def test_csp_header_in_response(client):
    response = client.get("/en/")
    assert response.status_code == 200

    csp_header = response.headers.get("Content-Security-Policy")
    assert csp_header is not None
    assert "default-src 'self'" in csp_header
    assert "frame-ancestors 'none'" in csp_header


@pytest.mark.django_db
@override_settings(CSP_ENABLED=False)
def test_csp_header_disabled(client):
    response = client.get("/en/")
    assert response.status_code == 200
    assert "Content-Security-Policy" not in response.headers
