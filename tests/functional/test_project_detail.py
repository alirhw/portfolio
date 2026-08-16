import pytest
from django.urls import reverse

from apps.portfolio.models import Project, Technology


@pytest.fixture
def sample_technology(db):
    return Technology.objects.create(name="Python", slug="python")


@pytest.fixture
def published_project(db, sample_technology):
    project = Project.objects.create(
        title_en="High Performance Engine",
        title_fa="موتور با کارایی بالا",
        slug="high-perf-engine",
        description_en="Detailed technical overview.",
        description_fa="مرور فنی دقیق.",
        is_published=True,
        repository_url="https://github.com/example/engine",
        demo_url="https://engine.example.com",
    )
    project.technologies.add(sample_technology)
    return project


@pytest.fixture
def unpublished_project(db):
    return Project.objects.create(
        title_en="Confidential R&D Project",
        title_fa="پروژه محرمانه تحقیق و توسعه",
        slug="confidential-rnd",
        description_en="Confidential blueprints.",
        description_fa="طرح‌های محرمانه.",
        is_published=False,
    )


@pytest.mark.django_db
def test_published_project_returns_200_and_renders_content(client, published_project):
    url = reverse("portfolio:project_detail", kwargs={"slug": published_project.slug})
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["project"] == published_project

    content = response.content.decode()
    assert "High Performance Engine" in content
    assert "Detailed technical overview." in content


@pytest.mark.django_db
def test_unpublished_project_strictly_returns_404(client, unpublished_project):
    # حتی با اسلاگ کاملاً درست، داده نباید به لایه قالب برسد
    url = reverse("portfolio:project_detail", kwargs={"slug": unpublished_project.slug})
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_unpublishing_live_project_immediately_returns_404(client, published_project):
    url = reverse("portfolio:project_detail", kwargs={"slug": published_project.slug})

    # مرحله ۱: ابتدا منتشر و در دسترس است
    initial_response = client.get(url)
    assert initial_response.status_code == 200

    # مرحله ۲: تغییر وضعیت به Unpublished در دیتابیس
    published_project.is_published = False
    published_project.save()

    # مرحله ۳: درخواست بعدی باید بلافاصله 404 شود
    updated_response = client.get(url)
    assert updated_response.status_code == 404


@pytest.mark.django_db
def test_nonexistent_slug_returns_404(client):
    url = reverse("portfolio:project_detail", kwargs={"slug": "invalid-random-slug-999"})
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
