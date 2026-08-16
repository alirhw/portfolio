import json

import pytest
from django.urls import reverse

from apps.portfolio.models import (
    PortfolioProfile,
    Project,
    Skill,
    SkillCategory,
    Technology,
)


@pytest.fixture
def terminal_seed_data(db):
    profile = PortfolioProfile.objects.create(
        full_name_en="Ali Developer",
        full_name_fa="علی دولوپر",
        headline_en="Backend Developer",
        headline_fa="توسعه‌دهنده بک‌اند",
        bio_en="Bio",
        bio_fa="بیوگرافی",
        email="ali@example.com",
        github_url="https://github.com/alidev",
        linkedin_url="https://linkedin.com/in/alidev",
        available_for_hire=True,
    )
    category = SkillCategory.objects.create(name_en="Backend", name_fa="بک‌اند")
    Skill.objects.create(
        name_en="Python",
        name_fa="پایتون",
        category=category,
        highlight=True,
    )

    tech = Technology.objects.create(name="Django", slug="django")
    project = Project.objects.create(
        title_en="Interactive System",
        title_fa="سیستم تعاملی",
        description_en="A real-time service",
        description_fa="یک سرویس بی‌درنگ",
        slug="interactive-system",
        is_published=True,
    )
    project.technologies.add(tech)

    return profile


@pytest.mark.django_db
def test_terminal_data_source_json_script_rendered_correctly(client, terminal_seed_data):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()

    # Verify json_script tag presence
    assert '<script id="terminal-data-source" type="application/json">' in html

    # Extract JSON content from script tag and validate
    start_tag = '<script id="terminal-data-source" type="application/json">'
    end_tag = "</script>"
    start_idx = html.find(start_tag) + len(start_tag)
    end_idx = html.find(end_tag, start_idx)
    raw_json = html[start_idx:end_idx]

    data = json.loads(raw_json)

    assert data["contact"]["name"] == "Ali Developer"
    assert data["contact"]["email"] == "ali@example.com"
    assert len(data["skills"]) == 1
    assert data["skills"][0]["category"] == "Backend"
    assert "Python" in data["skills"][0]["skills"]
    assert len(data["projects"]) == 1
    assert data["projects"][0]["title"] == "Interactive System"
    assert "Django" in data["projects"][0]["technologies"]


@pytest.mark.django_db
def test_progressive_enhancement_classes_present(client):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()
    assert "js-only-feature" in html
