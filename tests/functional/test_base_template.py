import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_homepage_uses_base_template(client):
    response = client.get("/")
    assert response.status_code == 200

    template_names = [template.name for template in response.templates]
    assert "base.html" in template_names
    assert "portfolio/home.html" in template_names


@pytest.mark.django_db
def test_navigation_contains_home_link(client):
    response = client.get("/")
    assert response.status_code == 200

    html = response.content.decode()
    assert 'href="/"' in html


def test_home_navigation_url_is_correct():
    assert reverse("portfolio:home") == "/"


@pytest.mark.django_db
def test_base_template_defines_theme_attribute(client):
    response = client.get("/")
    assert response.status_code == 200

    html = response.content.decode()
    assert 'data-theme="light"' in html


@pytest.mark.django_db
def test_base_template_contains_basic_seo_metadata(client):
    response = client.get("/")
    assert response.status_code == 200

    html = response.content.decode()
    assert '<meta charset="UTF-8">' in html
    assert 'name="viewport"' in html
    assert 'name="description"' in html
    assert 'name="robots"' in html


@pytest.mark.django_db
def test_navigation_contains_section_links(client):
    response = client.get("/")
    assert response.status_code == 200

    html = response.content.decode()
    assert 'href="#skills"' in html
    assert 'href="#experience"' in html
    assert 'href="#education"' in html
    assert 'href="#projects"' in html
    assert 'id="theme-toggle"' in html
