from datetime import date

import pytest
from django.urls import reverse

from apps.portfolio.models import (
    Education,
    Experience,
    PortfolioProfile,
    Skill,
    SkillCategory,
)


@pytest.mark.django_db
def test_homepage_renders_all_content_sections_correctly(client):
    profile = PortfolioProfile.objects.create(
        full_name_en="Ali Developer",
        full_name_fa="علی توسعه‌دهنده",
        headline_en="Backend Engineer",
        headline_fa="مهندس بک‌اند",
        bio_en="Python & Django specialist",
        bio_fa="متخصص پایتون و جنگو",
        available_for_hire=True,
        github_url="https://github.com/alirhw",
        linkedin_url="https://linkedin.com/in/alirhw",
        email="ali.rouhani.2005@gmail.com",
    )
    category = SkillCategory.objects.create(name_en="Backend", name_fa="بک‌اند")
    Skill.objects.create(name_en="Python", name_fa="پایتون", category=category, highlight=True)
    Skill.objects.create(name_en="Django", name_fa="جنگو", category=category, highlight=True)

    Experience.objects.create(
        position_en="Senior Developer",
        position_fa="توسعه‌دهنده ارشد",
        company="Tech Corp",
        start_date=date(2023, 1, 1),
        description_en="Core architecture",
        description_fa="معماری هسته",
    )
    Education.objects.create(
        degree_en="B.Sc.",
        degree_fa="کارشناسی",
        field_of_study_en="Computer Science",
        field_of_study_fa="علوم کامپیوتر",
        institution_en="University",
        institution_fa="دانشگاه",
        start_year=2018,
        graduation_year=2022,
    )

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200

    html = response.content.decode()
    # Hero verification
    assert profile.full_name_en in html
    assert profile.headline_en in html
    assert "Available for hire" in html

    # Skills verification
    assert "Backend" in html
    assert "Python" in html
    assert "Django" in html

    # Timeline verification
    assert "Senior Developer" in html
    assert "Tech Corp" in html
    assert "Computer Science" in html


@pytest.mark.django_db
def test_experience_order_is_reverse_chronological(client):
    Experience.objects.create(
        position_en="Older Job",
        position_fa="شغل قدیمی",
        company="Old Corp",
        start_date=date(2020, 1, 1),
    )
    Experience.objects.create(
        position_en="Newer Job",
        position_fa="شغل جدید",
        company="New Corp",
        start_date=date(2023, 1, 1),
    )

    response = client.get(reverse("portfolio:home"))
    html = response.content.decode()

    pos_newer = html.find("Newer Job")
    pos_older = html.find("Older Job")

    assert pos_newer != -1 and pos_older != -1
    assert pos_newer < pos_older
