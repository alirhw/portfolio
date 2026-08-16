import pytest
from django.urls import reverse

from apps.portfolio.models import (
    PortfolioProfile,
    Project,
    Skill,
    SkillCategory,
    Technology,
)


@pytest.mark.django_db
def test_homepage_returns_200(client):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_homepage_renders_profile_information_from_database(client):
    profile = PortfolioProfile.objects.create(
        full_name_en="Ali Rouhani",
        full_name_fa="علی روحانی",
        headline_en="Senior Python Engineer and System Architect",
        headline_fa="مهندس ارشد پایتون و معمار سیستم",
        bio_en="Building scalable distributed backends.",
        bio_fa="طراحی و توسعه سیستم‌های توزیع‌شده با مقیاس‌پذیری بالا.",
        github_url="https://github.com/alirhw",
        linkedin_url="https://linkedin.com/in/alirhw",
        email="ali.rouhani.2005@gmail.com",
    )

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200
    html = response.content.decode()

    assert profile.full_name_en in html
    assert profile.headline_en in html


@pytest.mark.django_db
def test_homepage_visibility_filters_unpublished_projects(client):
    tech = Technology.objects.create(name="Django", slug="django")

    published_project = Project.objects.create(
        title_en="Live Enterprise Platform",
        title_fa="پلتفرم سازمانی لایو",
        slug="live-enterprise-platform",
        description_en="Production system handling 10k RPS",
        description_fa="سیستم عملیاتی با توان پاسخ‌دهی ۱۰ هزار درخواست",
        is_published=True,
    )
    published_project.technologies.add(tech)

    unpublished_project = Project.objects.create(
        title_en="Internal Confidential Prototype",
        title_fa="پروتوتایپ محرمانه داخلی",
        slug="internal-confidential-prototype",
        description_en="Not for public view",
        description_fa="غیرقابل نمایش به عموم",
        is_published=False,
    )
    unpublished_project.technologies.add(tech)

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200
    html = response.content.decode()

    # Published project and its technologies must be rendered
    assert published_project.title_en in html
    assert tech.name in html

    # Unpublished project must NOT be present in HTML
    assert unpublished_project.title_en not in html


@pytest.mark.django_db
def test_homepage_vertical_slice_has_bounded_queries(client, django_assert_num_queries):
    cat1 = SkillCategory.objects.create(name_en="Backend", name_fa="بک‌اند", order=1)
    cat2 = SkillCategory.objects.create(name_en="Infrastructure", name_fa="زیرساخت", order=2)

    tech1 = Technology.objects.create(name="Python", slug="python")
    tech2 = Technology.objects.create(name="PostgreSQL", slug="postgresql")
    tech3 = Technology.objects.create(name="Redis", slug="redis")

    PortfolioProfile.objects.create(
        full_name_en="Ali Rouhani",
        full_name_fa="علی روحانی",
        headline_en="Senior Python Engineer",
        headline_fa="مهندس ارشد پایتون",
        bio_en="Bio",
        bio_fa="بیو",
        github_url="https://github.com",
        linkedin_url="https://linkedin.com",
        email="ali@example.com",
    )

    # 4 Highlighted Skills across multiple categories
    for i in range(4):
        category = cat1 if i % 2 == 0 else cat2
        Skill.objects.create(
            name_en=f"Skill {i}",
            name_fa=f"مهارت {i}",
            category=category,
            highlight=True,
            order=i,
        )

    # 2 Non-highlighted Skills
    for i in range(4, 6):
        Skill.objects.create(
            name_en=f"Hidden Skill {i}",
            name_fa=f"مهارت مخفی {i}",
            category=cat1,
            highlight=False,
            order=i,
        )

    # 5 Published Projects with multiple technologies
    for i in range(5):
        p = Project.objects.create(
            title_en=f"Project {i}",
            title_fa=f"پروژه {i}",
            slug=f"project-{i}",
            description_en=f"Description {i}",
            description_fa=f"توضیحات {i}",
            is_published=True,
            order=i,
        )
        p.technologies.add(tech1, tech2, tech3)

    # 3 Draft Projects
    for i in range(5, 8):
        Project.objects.create(
            title_en=f"Draft Project {i}",
            title_fa=f"پروژه پیش‌نویس {i}",
            slug=f"draft-{i}",
            description_en=f"Draft Description {i}",
            description_fa=f"توضیحات {i}",
            is_published=False,
            order=i,
        )

    # Bounded query test:
    # 1. Profile query
    # 2. SkillCategory query
    # 3. SkillCategory prefetch skills
    # 4. Experience query
    # 5. Education query
    # 6. Projects query
    # 7. Technologies prefetch query
    with django_assert_num_queries(7):
        response = client.get(reverse("portfolio:home"))
        assert response.status_code == 200

        # Verify complete rendering in HTML
        html = response.content.decode()
        assert "Ali Rouhani" in html
        assert "Senior Python Engineer" in html
        for i in range(4):
            assert f"Skill {i}" in html
        for i in range(4, 6):
            assert f"Hidden Skill {i}" not in html
        for i in range(5):
            assert f"Project {i}" in html
        for i in range(5, 8):
            assert f"Draft Project {i}" not in html


@pytest.mark.django_db
def test_homepage_works_with_empty_database_integration(client):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200
    assert response.context["profile"] is None
    assert len(response.context["skills"]) == 0
    assert len(response.context["projects"]) == 0
