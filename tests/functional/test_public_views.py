from datetime import date

import pytest

from apps.portfolio.models import (
    CurrentlyBuilding,
    Education,
    Experience,
    PortfolioProfile,
    Project,
    Skill,
    SkillCategory,
    Technology,
)


@pytest.fixture
def populated_db(db):
    profile = PortfolioProfile.objects.create(
        full_name_en="Ali Developer",
        full_name_fa="علی توسعه‌دهنده",
        headline_en="Senior Backend Engineer",
        headline_fa="مهندس ارشد بک‌اند",
        bio_en="Designing resilient architectures",
        bio_fa="طراحی معماری‌های تاب‌آور",
        available_for_hire=True,
    )

    cat_backend = SkillCategory.objects.create(name_en="Backend", name_fa="بک‌اند")
    cat_devops = SkillCategory.objects.create(name_en="DevOps", name_fa="دواپس")

    Skill.objects.create(name_en="Python", name_fa="پایتون", category=cat_backend, highlight=True)
    Skill.objects.create(name_en="Django", name_fa="جنگو", category=cat_backend, highlight=True)
    Skill.objects.create(name_en="Docker", name_fa="داکر", category=cat_devops, highlight=True)
    Skill.objects.create(
        name_en="Kubernetes", name_fa="کوبرنتیز", category=cat_devops, highlight=False
    )

    tech_py = Technology.objects.create(name="Python", slug="python")
    tech_dj = Technology.objects.create(name="Django", slug="django")

    for i in range(8):
        proj = Project.objects.create(
            title_en=f"Project {i}",
            title_fa=f"پروژه {i}",
            slug=f"project-{i}",
            description_en=f"Summary for project {i}",
            description_fa=f"توضیحات پروژه {i}",
            is_published=(i < 6),
            is_featured=(i == 0),
        )
        proj.technologies.add(tech_py, tech_dj)

    Experience.objects.create(
        position_en="Backend Lead",
        position_fa="هد بک‌اند",
        company="Tech Solutions",
        start_date=date(2022, 1, 1),
        description_en="Core services development",
        description_fa="توسعه سرویس‌های اصلی",
    )
    Education.objects.create(
        degree_en="B.Sc.",
        degree_fa="کارشناسی",
        field_of_study_en="Software Engineering",
        field_of_study_fa="مهندسی نرم‌افزار",
        institution_en="University",
        institution_fa="دانشگاه",
        start_year=2017,
        graduation_year=2021,
    )
    CurrentlyBuilding.objects.create(
        title_en="Privacy Pipeline",
        title_fa="خط لوله حریم خصوصی",
        description_en="Local regex and LLM redaction engine",
        description_fa="موتور ریداکشن محلی",
        progress_percentage=75,
        is_active=True,
    )

    return profile


@pytest.mark.django_db
def test_homepage_query_budget_is_strictly_bounded(client, django_assert_num_queries, populated_db):
    # ممیزی سرتاسری تعداد کوئری‌ها روی زبان پیش‌فرض
    with django_assert_num_queries(8):
        response = client.get("/en/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_i18n_language_cookie_and_attributes_rendering(client, populated_db):
    # تست زبان انگلیسی
    response_en = client.get("/en/")
    html_en = response_en.content.decode()
    assert 'lang="en"' in html_en
    assert 'dir="ltr"' in html_en
    assert "Featured Projects" in html_en

    # تست زبان فارسی
    response_fa = client.get("/fa/")
    html_fa = response_fa.content.decode()
    assert 'lang="fa"' in html_fa
    assert 'dir="rtl"' in html_fa
    assert "پروژه‌ها" in html_fa


@pytest.mark.django_db
def test_regression_core_elements_rendered_in_both_languages(client, populated_db):
    for lang_code in ["en", "fa"]:
        response = client.get(f"/{lang_code}/")
        assert response.status_code == 200
        html = response.content.decode()

        # هدر و لوگو
        assert "ALI.DEV" in html
        assert 'id="theme-toggle"' in html

        # داده‌های محتوایی
        assert "Ali Developer" in html
        assert "Senior Backend Engineer" in html
        assert "Python" in html
        assert "Docker" in html
        assert "Kubernetes" not in html  # highlight=False
        assert "Tech Solutions" in html
        assert "Software Engineering" in html
        assert "Privacy Pipeline" in html
        assert "Project 0" in html

        # محدودیت انتشار
        assert "Project 7" not in html  # Unpublished

        # فوتر
        assert "©" in html
