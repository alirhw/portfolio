import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_terminal_structure_and_safe_payload_present(client):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()

    # Confirm presence of terminal DOM structure
    assert 'id="portfolio-terminal"' in html
    assert 'id="terminal-input"' in html
    assert 'id="terminal-output"' in html

    # Confirm safe JSON payload type
    assert '<script id="terminal-payload" type="application/json">' in html
    assert "eval(" not in html
