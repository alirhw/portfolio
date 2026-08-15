import pytest
from django.contrib.admin.sites import site
from django.test import RequestFactory

from apps.contact.admin import ContactMessageAdmin
from apps.contact.models import ContactMessage
from apps.portfolio.admin import (
    PortfolioProfileAdmin,
    ProjectAdmin,
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


def test_contact_message_admin_configuration(request_factory):
    admin = ContactMessageAdmin(ContactMessage, site)
    request = request_factory.get("/admin/contact/contactmessage/")

    # Cannot add contact messages from admin
    assert admin.has_add_permission(request) is False

    # is_read is editable, others are read-only
    assert "is_read" in admin.list_editable
    assert "name" in admin.readonly_fields
    assert "email" in admin.readonly_fields
    assert "message" in admin.readonly_fields
    assert "ip_address" in admin.readonly_fields
    assert "created_at" in admin.readonly_fields
    assert "is_read" not in admin.readonly_fields
