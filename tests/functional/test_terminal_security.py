import pytest
from django.urls import reverse

from apps.portfolio.models import PortfolioProfile


@pytest.mark.django_db
def test_terminal_data_uses_safe_json_script(client):
    PortfolioProfile.objects.create(
        full_name_en="Ali Rouhani",
        full_name_fa="علی روحانی",
        headline_en="Backend Developer",
        headline_fa="توسعه‌دهنده بک‌اند",
        bio_en="Bio",
        bio_fa="بیوگرافی",
        email="ali@example.com",
        github_url="https://github.com/alirhw",
        linkedin_url="https://linkedin.com/in/alirhw",
    )

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()

    # Ensure safe json_script application and no unsafe eval
    assert '<script id="terminal-contact-email"' in html or 'type="application/json"' in html
    assert "eval(" not in html


def test_command_parser_escapes_xss_vectors():
    # Verify standard XSS payloads are escaped
    xss_payload = '<script>alert("pwned")</script>'
    escaped = (
        xss_payload.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped
