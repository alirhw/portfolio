import pytest
from django.urls import reverse

from apps.portfolio.models import PortfolioProfile, Project, Skill, SkillCategory, Technology


@pytest.mark.django_db
def test_homepage_loads_profile(client):
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

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200
    assert response.context["profile"] == profile
    assert "Ali Rouhani" in response.content.decode()


@pytest.mark.django_db
def test_homepage_only_returns_highlighted_skills(client):
    category = SkillCategory.objects.create(name_en="Backend", name_fa="بک‌اند", order=1)
    python = Skill.objects.create(
        name_en="Python",
        name_fa="پایتون",
        category=category,
        highlight=True,
    )
    django = Skill.objects.create(
        name_en="Django",
        name_fa="جنگو",
        category=category,
        highlight=True,
    )
    docker = Skill.objects.create(
        name_en="Docker",
        name_fa="داکر",
        category=category,
        highlight=False,
    )

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200
    skills = list(response.context["skills"])

    assert python in skills
    assert django in skills
    assert docker not in skills


@pytest.mark.django_db
def test_homepage_only_returns_published_projects(client):
    published_project = Project.objects.create(
        title_en="Public Project",
        title_fa="پروژه عمومی",
        slug="public-project",
        description_en="Public Description",
        description_fa="توضیحات عمومی",
        is_published=True,
    )
    unpublished_project = Project.objects.create(
        title_en="Draft Project",
        title_fa="پروژه پیش‌نویس",
        slug="draft-project",
        description_en="Draft Description",
        description_fa="توضیحات پیش‌نویس",
        is_published=False,
    )

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200
    projects = list(response.context["projects"])

    assert published_project in projects
    assert unpublished_project not in projects


@pytest.mark.django_db
def test_homepage_limits_projects_to_six(client):
    for i in range(1, 8):
        Project.objects.create(
            title_en=f"Project {i}",
            title_fa=f"پروژه {i}",
            slug=f"project-{i}",
            description_en=f"Description {i}",
            description_fa=f"توضیحات {i}",
            is_published=True,
            order=i,
        )

    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200
    projects = list(response.context["projects"])

    assert len(projects) == 6


@pytest.mark.django_db
def test_homepage_prefetches_project_technologies(client, django_assert_num_queries):
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

    for i in range(3):
        Skill.objects.create(
            name_en=f"Skill {i}",
            name_fa=f"مهارت {i}",
            category=category,
            highlight=True,
        )

    for i in range(4):
        p = Project.objects.create(
            title_en=f"Project {i}",
            title_fa=f"پروژه {i}",
            slug=f"project-{i}",
            description_en=f"Description {i}",
            description_fa=f"توضیحات {i}",
            is_published=True,
        )
        p.technologies.add(tech1, tech2)

    # 1. Profile query
    # 2. Skills query (select_related category)
    # 3. Projects query (published[:6])
    # 4. Technologies prefetch query
    with django_assert_num_queries(4):
        response = client.get(reverse("portfolio:home"))
        assert response.status_code == 200
        # Iterate over prefetch and foreign keys in context to ensure no N+1 triggers
        for s in response.context["skills"]:
            _ = s.category.name_en
        for p in response.context["projects"]:
            _ = [t.name for t in p.technologies.all()]


@pytest.mark.django_db
def test_homepage_works_with_empty_database(client):
    response = client.get(reverse("portfolio:home"))
    assert response.status_code == 200
    assert response.context["profile"] is None
    assert not list(response.context["skills"])
    assert not list(response.context["projects"])
