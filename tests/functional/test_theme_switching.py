import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_base_template_contains_theme_toggle_button_and_initial_attribute(client):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()

    # Presence of theme toggle button with unique ID and ARIA attributes
    assert 'id="theme-toggle"' in html
    assert "aria-label=" in html

    # Presence of FOIT prevention script in head
    assert "portfolio_theme" in html
    assert "data-theme" in html


@pytest.mark.django_db
def test_static_theme_module_linked(client):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()

    # Ensure main.js module is loaded
    assert "main.js" in html
