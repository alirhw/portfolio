import pytest
from django.test import override_settings

from apps.portfolio.models import Project
from apps.portfolio.sitemaps import ProjectSitemap, StaticViewSitemap


@pytest.mark.django_db
def test_robots_txt_renders_valid_content(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "text/plain" in response["Content-Type"]

    content = response.content.decode()
    assert "User-agent: *" in content
    assert "Disallow: /admin/" in content
    assert "Disallow: /contact/submit/" in content
    assert "Sitemap: " in content


@pytest.mark.django_db
def test_sitemap_xml_contains_published_projects(client):
    Project.objects.create(
        title_en="SEO Indexed App",
        title_fa="برنامه سئو شده",
        slug="seo-indexed-app",
        description_en="A discoverable project",
        description_fa="یک پروژه قابل کشف",
        is_published=True,
    )

    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert (
        "application/xml" in response["Content-Type"]
        or "text/xml" in response["Content-Type"]
    )

    content = response.content.decode()
    assert "/seo-indexed-app" in content


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_custom_404_error_page_renders_cleanly(client):
    response = client.get("/non-existent-page-url/")
    assert response.status_code == 404

    html = response.content.decode()
    assert "404" in html
    assert "Page Not Found" in html


def test_sitemap_classes_metadata():
    static_sitemap = StaticViewSitemap()
    assert static_sitemap.priority == 1.0
    assert static_sitemap.changefreq == "weekly"
    assert "portfolio:home" in static_sitemap.items()

    project_sitemap = ProjectSitemap()
    assert project_sitemap.priority == 0.8
    assert project_sitemap.changefreq == "monthly"
