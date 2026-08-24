import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_skip_link_exists_in_base_template(client):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()
    assert "skip-link" in html or "skip-to-content" in html
    assert 'href="#main-content"' in html


@pytest.mark.django_db
def test_accessibility_landmarks_and_roles_present(client):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()
    # Semantic & ARIA Landmarks
    assert 'role="banner"' in html
    assert 'role="main"' in html
    assert 'role="contentinfo"' in html
    assert "aria-label=" in html


@pytest.mark.django_db
def test_viewport_meta_tag_allows_scaling(client):
    response = client.get(reverse("portfolio:home"))
    html = response.content.decode()

    # Verify user scaling is allowed (WCAG accessibility standard)
    assert 'name="viewport"' in html
    assert "width=device-width" in html
    assert "user-scalable=no" not in html
