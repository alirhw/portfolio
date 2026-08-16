import pytest
from django.urls import reverse

from apps.portfolio.models import Project, Technology


@pytest.fixture
def published_project(db):
    tech = Technology.objects.create(name="Django", slug="django")
    project = Project.objects.create(
        title_en="Distributed Task Queue",
        title_fa="صف وظایف توزیع‌شده",
        slug="distributed-task-queue",
        description_en="Detailed technical architectural decisions and performance metrics.",
        description_fa="تصمیمات معماری فنی دقیق و معیارهای کارایی.",
        is_published=True,
        repository_url="https://github.com/example/queue",
        demo_url="https://queue.example.com",
    )
    project.technologies.add(tech)
    return project


@pytest.fixture
def draft_project(db):
    return Project.objects.create(
        title_en="Unreleased Internal Tool",
        title_fa="ابزار داخلی منتشرنشده",
        slug="unreleased-tool",
        description_en="Not ready for public eye.",
        description_fa="آماده مشاهده عمومی نیست.",
        is_published=False,
    )


@pytest.mark.django_db
def test_published_project_detail_returns_200(client, published_project):
    url = reverse("portfolio:project_detail", kwargs={"slug": published_project.slug})
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["project"] == published_project

    html = response.content.decode()
    assert published_project.title in html
    assert published_project.summary in html
    assert "Distributed Task Queue" in html
    assert "Django" in html
    assert "https://github.com/example/queue" in html


@pytest.mark.django_db
def test_unpublished_project_detail_returns_404(client, draft_project):
    url = reverse("portfolio:project_detail", kwargs={"slug": draft_project.slug})
    response = client.get(url)

    # تضمین امنیتی: پروژه غیرمنتشر نباید حتی با داشتن slug معتبر قابل مشاهده باشد
    assert response.status_code == 404


@pytest.mark.django_db
def test_nonexistent_project_slug_returns_404(client):
    url = reverse("portfolio:project_detail", kwargs={"slug": "does-not-exist"})
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_project_detail_query_count_is_bounded(
    client, django_assert_num_queries, published_project
):
    url = reverse("portfolio:project_detail", kwargs={"slug": published_project.slug})

    # کوئری واکشی پروژه + کوئری پیش‌بارگذاری فناوری‌ها
    with django_assert_num_queries(2):
        response = client.get(url)

    assert response.status_code == 200
