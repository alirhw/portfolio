from django.urls import reverse


def test_home_page_is_available(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_page_uses_portfolio_template(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "portfolio/home.html" in [t.name for t in response.templates]


def test_home_url_resolves():
    assert reverse("portfolio:home") == "/"
