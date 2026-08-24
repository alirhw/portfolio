import pytest
from django.urls import reverse

from apps.portfolio.models import CurrentlyBuilding, Project, Technology


@pytest.mark.django_db
def test_projects_and_currently_building_rendered(client):
    tech = Technology.objects.create(name="Django", slug="django")
    project = Project.objects.create(
        title_en="OpenSource Portfolio",
        title_fa="پورتفولیو",
        slug="opensource-portfolio",
        description_en="A clean portfolio builder",
        description_fa="توضیحات",
        is_published=True,
        is_featured=True,
        repository_url="https://github.com/example/repo",
        demo_url="https://example.com",
    )
    project.technologies.add(tech)

    CurrentlyBuilding.objects.create(
        title_en="LLM Pipeline Tool",
        title_fa="ابزار خط لوله",
        description_en="Hybrid regex + local model redaction",
        description_fa="توضیحات",
        progress_percentage=60,
        is_active=True,
    )

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()

    # Projects verification
    assert ("OpenSource Portfolio" in html) or ("پورتفولیو" in html)
    assert "Django" in html
    assert ("Featured" in html) or ("منتخب" in html)
    assert "https://github.com/example/repo" in html
    assert "https://example.com" in html

    # Currently building verification
    assert ("Currently Building" in html) or ("در حال ساخت" in html)
    assert ("LLM Pipeline Tool" in html) or ("ابزار خط لوله" in html)
    assert "60%" in html


@pytest.mark.django_db
def test_inactive_currently_building_not_rendered(client):
    CurrentlyBuilding.objects.create(
        title_en="Archived Task",
        title_fa="تسک آرشیو شده",
        description_en="Not currently active",
        description_fa="غیرفعال",
        is_active=False,
    )

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200
    assert "Archived Task" not in response.content.decode()
