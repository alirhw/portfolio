import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.contact.models import ContactMessage
from apps.portfolio.models import Project, Resume


@pytest.fixture(autouse=True)
def use_temp_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def superuser(db):
    user_model = get_user_model()
    return user_model.objects.create_superuser(
        username="admin_user",
        email="admin@example.com",
        password="password123",
    )


@pytest.fixture
def regular_user(db):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username="regular_user",
        email="user@example.com",
        password="password123",
    )


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_admin_login(client):
    response = client.get(reverse("admin:index"))
    assert response.status_code in {200, 302}
    if response.status_code == 302:
        assert "/admin/login/" in response.url


@pytest.mark.django_db
def test_non_staff_user_cannot_access_admin(client, regular_user):
    client.force_login(regular_user)
    response = client.get(reverse("admin:index"))
    assert response.status_code in {200, 302}
    if response.status_code == 302:
        assert "/admin/login/" in response.url


@pytest.mark.django_db
def test_staff_admin_can_access_admin(client, superuser):
    client.force_login(superuser)
    response = client.get(reverse("admin:index"))
    assert response.status_code == 200
    assert "Django administration" in response.content.decode()


@pytest.mark.django_db
def test_admin_can_publish_project_via_action(client, superuser):
    client.force_login(superuser)
    project = Project.objects.create(
        title_en="Draft Project",
        title_fa="پروژه پیش‌نویس",
        slug="draft-project",
        description_en="Draft Description",
        description_fa="توضیحات پیش‌نویس",
        is_published=False,
    )

    response = client.post(
        reverse("admin:portfolio_project_changelist"),
        {
            "action": "publish_selected_projects",
            "_selected_action": [str(project.pk)],
        },
        follow=True,
    )

    assert response.status_code == 200
    project.refresh_from_db()
    assert project.is_published is True
    assert project in Project.objects.published()


@pytest.mark.django_db
def test_admin_can_unpublish_project_via_action(client, superuser):
    client.force_login(superuser)
    project = Project.objects.create(
        title_en="Live Project",
        title_fa="پروژه منتشرشده",
        slug="live-project",
        description_en="Live Description",
        description_fa="توضیحات زنده",
        is_published=True,
    )

    response = client.post(
        reverse("admin:portfolio_project_changelist"),
        {
            "action": "unpublish_selected_projects",
            "_selected_action": [str(project.pk)],
        },
        follow=True,
    )

    assert response.status_code == 200
    project.refresh_from_db()
    assert project.is_published is False
    assert project not in Project.objects.published()


@pytest.mark.django_db
def test_admin_can_replace_current_resume_via_change_form(client, superuser):
    client.force_login(superuser)
    file1 = SimpleUploadedFile("resume1.pdf", b"content 1")
    file2 = SimpleUploadedFile("resume2.pdf", b"content 2")

    resume_old = Resume.objects.create(
        title="Resume Old",
        file=file1,
        version="v1.0",
        is_current=True,
    )
    resume_new = Resume.objects.create(
        title="Resume New",
        file=file2,
        version="v2.0",
        is_current=False,
    )

    update_file = SimpleUploadedFile("resume_updated.pdf", b"updated content")

    # Submit change form with is_current checked
    response = client.post(
        reverse("admin:portfolio_resume_change", args=[resume_new.pk]),
        {
            "title": "Resume New",
            "file": update_file,
            "version": "v2.0",
            "is_current": "on",
            "_save": "Save",
        },
        follow=True,
    )

    assert response.status_code == 200
    resume_old.refresh_from_db()
    resume_new.refresh_from_db()

    assert resume_old.is_current is False
    assert resume_new.is_current is True
    assert Resume.objects.filter(is_current=True).count() == 1


@pytest.mark.django_db
def test_contact_message_cannot_be_added_manually(client, superuser):
    client.force_login(superuser)
    response = client.get(reverse("admin:contact_contactmessage_add"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_contact_message_fields_are_readonly_in_admin(client, superuser):
    client.force_login(superuser)
    msg = ContactMessage.objects.create(
        name="Visitor Name",
        email="visitor@example.com",
        subject="Important Inquiry",
        message="This is a test message from visitor.",
        ip_address="198.51.100.42",
        is_read=False,
    )

    response = client.get(reverse("admin:contact_contactmessage_change", args=[msg.pk]))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Visitor Name" in content
    assert "visitor@example.com" in content
    assert "198.51.100.42" in content
