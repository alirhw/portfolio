import pytest
from django.urls import reverse
from django.utils import translation


@pytest.mark.django_db
def test_homepage_uses_base_template(client):
    with translation.override("en"):
        home_url = reverse("portfolio:home")
    response = client.get(home_url)
    assert response.status_code == 200

    template_names = [template.name for template in response.templates]
    assert "base.html" in template_names
    assert "portfolio/home.html" in template_names


@pytest.mark.django_db
def test_navigation_contains_home_link(client):
    with translation.override("en"):
        home_url = reverse("portfolio:home")
    response = client.get(home_url)
    assert response.status_code == 200

    html = response.content.decode()
    assert f'href="{home_url}"' in html


def test_home_navigation_url_is_correct():
    with translation.override("en"):
        assert reverse("portfolio:home") == "/en/"


@pytest.mark.django_db
def test_base_template_defines_theme_attribute(client):
    with translation.override("en"):
        home_url = reverse("portfolio:home")
    response = client.get(home_url)
    assert response.status_code == 200

    html = response.content.decode()
    assert 'data-theme="light"' in html


@pytest.mark.django_db
def test_base_template_contains_basic_seo_metadata(client):
    with translation.override("en"):
        home_url = reverse("portfolio:home")
    response = client.get(home_url)
    assert response.status_code == 200

    html = response.content.decode()
    assert '<meta charset="UTF-8">' in html
    assert 'name="viewport"' in html
    assert 'name="description"' in html
    assert 'name="robots"' in html


@pytest.mark.django_db
def test_navigation_contains_section_links(client):
    with translation.override("en"):
        home_url = reverse("portfolio:home")
    response = client.get(home_url)
    assert response.status_code == 200

    html = response.content.decode()
    assert 'href="#skills"' in html
    assert 'href="#building"' in html
    assert 'href="#projects"' in html
    assert 'href="#github-stats"' in html
    assert 'href="#contact"' in html
    assert 'id="theme-toggle"' in html
