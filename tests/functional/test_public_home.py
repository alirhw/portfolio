import pytest
from django.urls import reverse
from django.utils import translation


@pytest.mark.django_db
def test_home_page_is_available(client):
    with translation.override("en"):
        home_url = reverse("portfolio:home")
    response = client.get(home_url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_page_uses_portfolio_template(client):
    with translation.override("en"):
        home_url = reverse("portfolio:home")
    response = client.get(home_url)
    assert response.status_code == 200
    assert "portfolio/home.html" in [t.name for t in response.templates]


def test_home_url_resolves():
    with translation.override("en"):
        assert reverse("portfolio:home") == "/en/"
