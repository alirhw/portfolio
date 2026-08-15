import pytest
from django.db import IntegrityError

from apps.portfolio.models import Project, Technology


@pytest.mark.django_db
def test_published_manager_returns_only_published_projects():
    published = Project.objects.create(
        title_en="Portfolio App",
        title_fa="پروژه پورتفولیو",
        slug="portfolio-app",
        description_en="Portfolio project description.",
        description_fa="توضیحات پروژه پورتفولیو.",
        is_published=True,
    )
    draft = Project.objects.create(
        title_en="Secret Project",
        title_fa="پروژه محرمانه",
        slug="secret-project",
        description_en="Draft description.",
        description_fa="توضیحات پیش‌نویس.",
        is_published=False,
    )

    published_list = list(Project.published_objects.all())
    assert published in published_list
    assert draft not in published_list


@pytest.mark.django_db
def test_published_queryset_filters_unpublished_projects():
    published = Project.objects.create(
        title_en="Public Blog",
        title_fa="وبلاگ عمومی",
        slug="public-blog",
        description_en="Public blog description.",
        description_fa="توضیحات وبلاگ.",
        is_published=True,
    )
    draft = Project.objects.create(
        title_en="Internal Tool",
        title_fa="ابزار داخلی",
        slug="internal-tool",
        description_en="Internal tool description.",
        description_fa="توضیحات ابزار داخلی.",
        is_published=False,
    )

    qs_published = Project.objects.published()
    assert published in qs_published
    assert draft not in qs_published


@pytest.mark.django_db
def test_featured_and_draft_isolation():
    featured_published = Project.objects.create(
        title_en="Featured Public",
        title_fa="پروژه ویژه عمومی",
        slug="featured-public",
        description_en="Featured public description.",
        description_fa="توضیحات ویژه عمومی.",
        is_published=True,
        is_featured=True,
    )
    featured_draft = Project.objects.create(
        title_en="Featured Draft",
        title_fa="پروژه ویژه پیش‌نویس",
        slug="featured-draft",
        description_en="Featured draft description.",
        description_fa="توضیحات ویژه پیش‌نویس.",
        is_published=False,
        is_featured=True,
    )

    public_featured = list(Project.published_objects.featured())
    assert featured_published in public_featured
    assert featured_draft not in public_featured


@pytest.mark.django_db
def test_project_slug_is_unique():
    Project.objects.create(
        title_en="Project One",
        title_fa="پروژه یک",
        slug="duplicate-slug",
        description_en="Description one.",
        description_fa="توضیحات یک.",
    )

    with pytest.raises(IntegrityError):
        Project.objects.create(
            title_en="Project Two",
            title_fa="پروژه دو",
            slug="duplicate-slug",
            description_en="Description two.",
            description_fa="توضیحات دو.",
        )


@pytest.mark.django_db
def test_project_custom_ordering():
    p2 = Project.objects.create(
        title_en="Second Project",
        title_fa="پروژه دوم",
        slug="second-project",
        description_en="Second description.",
        description_fa="توضیحات دوم.",
        is_published=True,
        order=2,
    )
    p1 = Project.objects.create(
        title_en="First Project",
        title_fa="پروژه اول",
        slug="first-project",
        description_en="First description.",
        description_fa="توضیحات اول.",
        is_published=True,
        order=1,
    )

    ordered_projects = list(Project.published_objects.all())
    assert ordered_projects == [p1, p2]


@pytest.mark.django_db
def test_project_technologies_relationship():
    tech_python = Technology.objects.create(name="Python", slug="python")
    tech_django = Technology.objects.create(name="Django", slug="django")

    project = Project.objects.create(
        title_en="Backend API",
        title_fa="ای‌پی‌آی بک‌اند",
        slug="backend-api",
        description_en="API description.",
        description_fa="توضیحات ای‌پی‌آی.",
        demo_url="https://demo.example.com",
        repository_url="https://github.com/example/api",
        is_published=True,
    )
    project.technologies.add(tech_python, tech_django)

    assert project.technologies.count() == 2
    assert tech_python in project.technologies.all()
    assert tech_django in project.technologies.all()
    assert project in tech_python.projects.all()
    assert str(project) == "Backend API"
