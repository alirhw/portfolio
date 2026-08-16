from unittest.mock import MagicMock

import pytest
from django.contrib.admin.sites import site
from django.test import RequestFactory

from apps.contact.admin import ContactMessageAdmin
from apps.contact.models import ContactMessage
from apps.portfolio.admin import (
    PortfolioProfileAdmin,
    ProjectAdmin,
    ResumeAdmin,
    SkillAdmin,
)
from apps.portfolio.models import (
    CurrentlyBuilding,
    Education,
    Experience,
    PortfolioProfile,
    Project,
    Resume,
    Skill,
    SkillCategory,
    Technology,
)


@pytest.fixture
def request_factory():
    return RequestFactory()


def test_all_domain_models_registered_in_admin():
    registered_models = site._registry
    assert PortfolioProfile in registered_models
    assert SkillCategory in registered_models
    assert Skill in registered_models
    assert Technology in registered_models
    assert Project in registered_models
    assert Experience in registered_models
    assert Education in registered_models
    assert CurrentlyBuilding in registered_models
    assert Resume in registered_models
    assert ContactMessage in registered_models


@pytest.mark.django_db
def test_portfolio_profile_admin_has_add_permission(request_factory):
    admin = PortfolioProfileAdmin(PortfolioProfile, site)
    request = request_factory.get("/admin/portfolio/portfolioprofile/")

    # 0 profiles -> add allowed
    assert admin.has_add_permission(request) is True

    # 1 profile -> add disabled
    PortfolioProfile.objects.create(
        full_name_en="Ali",
        full_name_fa="علی",
        headline_en="Developer",
        headline_fa="توسعه‌دهنده",
        bio_en="Bio",
        bio_fa="بیو",
        github_url="https://github.com",
        linkedin_url="https://linkedin.com",
        email="ali@example.com",
    )
    assert admin.has_add_permission(request) is False


def test_skill_admin_configuration():
    admin = SkillAdmin(Skill, site)
    assert "order" in admin.list_editable
    assert "highlight" in admin.list_editable
    for field in admin.list_editable:
        assert field in admin.list_display


def test_project_admin_configuration():
    admin = ProjectAdmin(Project, site)
    assert "is_published" in admin.list_filter
    assert "technologies" in admin.list_filter
    assert "is_published" in admin.list_display
    assert "is_featured" in admin.list_display
    assert "slug" in admin.list_display
    assert "publish_selected_projects" in admin.actions
    assert "unpublish_selected_projects" in admin.actions


@pytest.mark.django_db
def test_project_admin_publish_and_unpublish_actions(request_factory):
    admin = ProjectAdmin(Project, site)
    request = request_factory.get("/admin/portfolio/project/")
    admin.message_user = MagicMock()

    p1 = Project.objects.create(
        title_en="P1",
        title_fa="پ۱",
        slug="p1",
        description_en="D1",
        description_fa="ت۱",
        is_published=False,
    )
    p2 = Project.objects.create(
        title_en="P2",
        title_fa="پ۲",
        slug="p2",
        description_en="D2",
        description_fa="ت۲",
        is_published=False,
    )

    qs = Project.objects.filter(id__in=[p1.id, p2.id])

    # 1. Test Publish Action
    admin.publish_selected_projects(request, qs)
    p1.refresh_from_db()
    p2.refresh_from_db()
    assert p1.is_published is True
    assert p2.is_published is True
    assert p1 in Project.objects.published()
    assert p2 in Project.objects.published()
    admin.message_user.assert_called_with(
        request,
        "2 project(s) published successfully.",
        25,  # messages.SUCCESS is 25
    )

    # 2. Test Unpublish Action
    admin.unpublish_selected_projects(request, qs)
    p1.refresh_from_db()
    p2.refresh_from_db()
    assert p1.is_published is False
    assert p2.is_published is False
    assert p1 not in Project.objects.published()
    assert p2 not in Project.objects.published()
    admin.message_user.assert_called_with(
        request,
        "2 project(s) unpublished successfully.",
        25,  # messages.SUCCESS is 25
    )


def test_contact_message_admin_configuration(request_factory):
    admin = ContactMessageAdmin(ContactMessage, site)
    request = request_factory.get("/admin/contact/contactmessage/")

    # Cannot add contact messages from admin
    assert admin.has_add_permission(request) is False

    # is_read is editable, others are read-only
    assert "is_read" in admin.list_editable
    assert "sender_name" in admin.readonly_fields or "name" in admin.readonly_fields
    assert "email" in admin.readonly_fields
    assert "message" in admin.readonly_fields
    assert "ip_address" in admin.readonly_fields
    assert "created_at" in admin.readonly_fields
    assert "is_read" not in admin.readonly_fields


@pytest.mark.django_db
def test_resume_admin_replaces_current_resume_safely(request_factory):
    admin = ResumeAdmin(Resume, site)
    request = request_factory.get("/admin/portfolio/resume/")

    resume_a = Resume.objects.create(
        title="Resume A",
        file="resumes/a.pdf",
        is_current=True,
    )
    resume_b = Resume.objects.create(
        title="Resume B",
        file="resumes/b.pdf",
        is_current=False,
    )

    resume_b.is_current = True
    admin.save_model(request, resume_b, form=None, change=True)

    resume_a.refresh_from_db()
    resume_b.refresh_from_db()
    assert resume_a.is_current is False
    assert resume_b.is_current is True
    assert Resume.objects.filter(is_current=True).count() == 1


@pytest.mark.django_db
def test_resume_admin_saves_non_current_resume_without_affecting_current(request_factory):
    admin = ResumeAdmin(Resume, site)
    request = request_factory.get("/admin/portfolio/resume/")

    resume_a = Resume.objects.create(
        title="Resume A",
        file="resumes/a.pdf",
        is_current=True,
    )
    resume_c = Resume(
        title="Resume C",
        file="resumes/c.pdf",
        is_current=False,
    )

    admin.save_model(request, resume_c, form=None, change=False)

    resume_a.refresh_from_db()
    resume_c.refresh_from_db()
    assert resume_a.is_current is True
    assert resume_c.is_current is False
    assert Resume.objects.filter(is_current=True).count() == 1


@pytest.mark.django_db
def test_resume_admin_edit_same_current_resume_keeps_current(request_factory):
    admin = ResumeAdmin(Resume, site)
    request = request_factory.get("/admin/portfolio/resume/")

    resume_a = Resume.objects.create(
        title="Resume A",
        file="resumes/a.pdf",
        is_current=True,
    )

    resume_a.title = "Resume A Updated"
    admin.save_model(request, resume_a, form=None, change=True)

    resume_a.refresh_from_db()
    assert resume_a.title == "Resume A Updated"
    assert resume_a.is_current is True
    assert Resume.objects.filter(is_current=True).count() == 1


@pytest.mark.django_db
def test_resume_admin_atomic_rollback_on_save_failure(request_factory, monkeypatch):
    admin = ResumeAdmin(Resume, site)
    request = request_factory.get("/admin/portfolio/resume/")

    resume_a = Resume.objects.create(
        title="Resume A",
        file="resumes/a.pdf",
        is_current=True,
    )
    resume_b = Resume.objects.create(
        title="Resume B",
        file="resumes/b.pdf",
        is_current=False,
    )

    resume_b.is_current = True

    def failing_save_model(self, req, obj, form, change):
        raise RuntimeError("Simulated database failure during save")

    from django.contrib.admin import ModelAdmin

    monkeypatch.setattr(ModelAdmin, "save_model", failing_save_model)

    with pytest.raises(RuntimeError, match="Simulated database failure"):
        admin.save_model(request, resume_b, form=None, change=True)

    resume_a.refresh_from_db()
    resume_b.refresh_from_db()
    # Transaction rollback guarantees Resume A stays True and Resume B stays False
    assert resume_a.is_current is True
    assert resume_b.is_current is False
    assert Resume.objects.filter(is_current=True).count() == 1
