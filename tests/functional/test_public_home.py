import pytest
from django.urls import reverse

from apps.portfolio.models import PortfolioProfile, Project, Skill, SkillCategory, Technology


@pytest.mark.django_db
def test_home_page_is_available(client):
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_page_uses_portfolio_template(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "portfolio/home.html" in [t.name for t in response.templates]


def test_home_url_resolves():
    assert reverse("portfolio:home") == "/"


@pytest.mark.django_db
def test_home_page_context_data(client):
    profile = PortfolioProfile.objects.create(
        full_name_en="Ali Rouhani",
        full_name_fa="علی روحانی",
        headline_en="Senior Python Engineer",
        headline_fa="مهندس ارشد پایتون",
        bio_en="Bio EN",
        bio_fa="بیو فارسی",
        github_url="https://github.com",
        linkedin_url="https://linkedin.com",
        email="ali@example.com",
    )

    category = SkillCategory.objects.create(name_en="Backend", name_fa="بک‌اند", order=1)
    skill_highlighted = Skill.objects.create(
        name_en="Django",
        name_fa="جنگو",
        category=category,
        highlight=True,
    )
    skill_hidden = Skill.objects.create(
        name_en="Bash",
        name_fa="بش",
        category=category,
        highlight=False,
    )

    tech = Technology.objects.create(name="PostgreSQL", slug="postgres")
    proj_published = Project.objects.create(
        title_en="Awesome App",
        title_fa="اپلیکیشن عالی",
        slug="awesome-app",
        description_en="Great product",
        description_fa="محصول عالی",
        is_published=True,
    )
    proj_published.technologies.add(tech)

    proj_draft = Project.objects.create(
        title_en="Secret Project",
        title_fa="پروژه مخفی",
        slug="secret-project",
        description_en="Top secret",
        description_fa="کاملا مخفی",
        is_published=False,
    )

    response = client.get("/")
    assert response.status_code == 200

    # Profile context assertion
    assert response.context["profile"] == profile
    assert "Ali Rouhani" in response.content.decode()
    assert "Senior Python Engineer" in response.content.decode()

    # Skills context assertion (only highlighted)
    skills = list(response.context["skills"])
    assert skill_highlighted in skills
    assert skill_hidden not in skills
    assert "Django" in response.content.decode()

    # Projects context assertion (only published, max 6)
    projects = list(response.context["projects"])
    assert proj_published in projects
    assert proj_draft not in projects
    assert "Awesome App" in response.content.decode()
    assert "PostgreSQL" in response.content.decode()
    assert "Secret Project" not in response.content.decode()


@pytest.mark.django_db
def test_home_page_query_optimization(client, django_assert_num_queries):
    category = SkillCategory.objects.create(name_en="Backend", name_fa="بک‌اند")
    tech1 = Technology.objects.create(name="Python", slug="python")
    tech2 = Technology.objects.create(name="Django", slug="django")

    PortfolioProfile.objects.create(
        full_name_en="Ali Rouhani",
        full_name_fa="علی روحانی",
        headline_en="Senior Python Engineer",
        headline_fa="مهندس ارشد پایتون",
        bio_en="Bio EN",
        bio_fa="بیو فارسی",
        github_url="https://github.com",
        linkedin_url="https://linkedin.com",
        email="ali@example.com",
    )

    for i in range(5):
        Skill.objects.create(
            name_en=f"Skill {i}",
            name_fa=f"مهارت {i}",
            category=category,
            highlight=True,
        )

    for i in range(5):
        p = Project.objects.create(
            title_en=f"Project {i}",
            title_fa=f"پروژه {i}",
            slug=f"project-{i}",
            description_en=f"Description {i}",
            description_fa=f"توضیحات {i}",
            is_published=True,
        )
        p.technologies.add(tech1, tech2)

    # Queries:
    # 1. PortfolioProfile.objects.first()
    # 2. Skill.objects.filter(highlight=True).select_related('category')
    # 3. Project.objects.published()[:6]
    # 4. prefetch_related('technologies')
    with django_assert_num_queries(4):
        response = client.get("/")
        assert response.status_code == 200
        # Iterate in context to trigger any potential lazy evaluation
        for s in response.context["skills"]:
            _ = s.category.name_en
        for p in response.context["projects"]:
            _ = list(p.technologies.all())
