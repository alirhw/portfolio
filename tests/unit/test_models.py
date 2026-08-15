import datetime

import pytest

from apps.contact.models import ContactMessage
from apps.portfolio.models import (
    CurrentlyBuilding,
    Education,
    Experience,
    Project,
    Skill,
    SkillCategory,
    Technology,
)


@pytest.fixture(autouse=True)
def use_temp_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.mark.django_db
def test_project_published_queryset_and_visibility():
    p1 = Project.objects.create(
        title_en="Live App",
        title_fa="اپلیکیشن فعال",
        slug="live-app",
        description_en="Live description",
        description_fa="توضیحات فعال",
        is_published=True,
    )
    p2 = Project.objects.create(
        title_en="Draft App",
        title_fa="اپلیکیشن پیش‌نویس",
        slug="draft-app",
        description_en="Draft description",
        description_fa="توضیحات پیش‌نویس",
        is_published=False,
    )

    published = list(Project.objects.published())
    assert p1 in published
    assert p2 not in published


@pytest.mark.django_db
def test_project_prefetch_technologies_prevents_n_plus_one(django_assert_num_queries):
    t1 = Technology.objects.create(name="Python", slug="python")
    t2 = Technology.objects.create(name="Django", slug="django")
    t3 = Technology.objects.create(name="PostgreSQL", slug="postgresql")

    p1 = Project.objects.create(
        title_en="Project 1",
        title_fa="پروژه ۱",
        slug="proj-1",
        description_en="Desc 1",
        description_fa="توضیحات ۱",
        is_published=True,
    )
    p1.technologies.add(t1, t2)

    p2 = Project.objects.create(
        title_en="Project 2",
        title_fa="پروژه ۲",
        slug="proj-2",
        description_en="Desc 2",
        description_fa="توضیحات ۲",
        is_published=True,
    )
    p2.technologies.add(t2, t3)

    # 1 query for projects + 1 query for technologies prefetch = 2 queries total
    with django_assert_num_queries(2):
        projects = list(Project.published_objects.with_technologies())
        for project in projects:
            _ = list(project.technologies.all())


@pytest.mark.django_db
def test_skill_select_related_category_prevents_n_plus_one(django_assert_num_queries):
    cat_backend = SkillCategory.objects.create(name_en="Backend", name_fa="بک‌اند")
    cat_frontend = SkillCategory.objects.create(name_en="Frontend", name_fa="فرانت‌اند")

    Skill.objects.create(
        name_en="Python",
        name_fa="پایتون",
        category=cat_backend,
    )
    Skill.objects.create(
        name_en="Django",
        name_fa="جنگو",
        category=cat_backend,
    )
    Skill.objects.create(
        name_en="Vue.js",
        name_fa="ویوجی‌اس",
        category=cat_frontend,
    )

    # 1 single JOIN query for skills + categories
    with django_assert_num_queries(1):
        skills = list(Skill.objects.with_category())
        for skill in skills:
            _ = skill.category.name_en


@pytest.mark.django_db
def test_skill_ordering_and_highlighted_filter():
    category = SkillCategory.objects.create(name_en="DevOps", name_fa="دواپس")
    s2 = Skill.objects.create(
        name_en="Kubernetes",
        name_fa="کوبرنتیز",
        category=category,
        highlight=False,
        order=2,
    )
    s1 = Skill.objects.create(
        name_en="Docker",
        name_fa="داکر",
        category=category,
        highlight=True,
        order=1,
    )

    ordered_skills = list(Skill.objects.filter(category=category))
    assert ordered_skills == [s1, s2]

    highlighted_skills = list(Skill.objects.highlighted())
    assert s1 in highlighted_skills
    assert s2 not in highlighted_skills


@pytest.mark.django_db
def test_experience_chronological_ordering():
    e2 = Experience.objects.create(
        position_en="Junior Dev",
        position_fa="برنامه‌نویس جونیور",
        company="Startup A",
        start_date=datetime.date(2020, 1, 1),
        end_date=datetime.date(2021, 12, 31),
    )
    e1 = Experience.objects.create(
        position_en="Senior Dev",
        position_fa="برنامه‌نویس ارشد",
        company="Company B",
        start_date=datetime.date(2022, 1, 1),
        is_current=True,
    )

    experiences = list(Experience.objects.all())
    assert experiences == [e1, e2]


@pytest.mark.django_db
def test_education_and_currently_building_primitives():
    edu = Education.objects.create(
        degree_en="B.Sc.",
        degree_fa="کارشناسی",
        institution_en="University",
        institution_fa="دانشگاه",
        graduation_year=2023,
    )
    cb = CurrentlyBuilding.objects.create(
        title_en="Open Source Tool",
        title_fa="ابزار متن‌باز",
        progress_percentage=80,
    )

    assert edu.pk is not None
    assert cb.pk is not None


@pytest.mark.django_db
def test_contact_message_query_primitives():
    m1 = ContactMessage.objects.create(
        name="User A",
        email="a@example.com",
        message="First message",
    )
    m2 = ContactMessage.objects.create(
        name="User B",
        email="b@example.com",
        message="Second message",
    )

    messages = list(ContactMessage.objects.all())
    assert messages == [m2, m1]  # Ordered by -created_at
