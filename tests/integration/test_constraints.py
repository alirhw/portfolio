import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.db.models import ProtectedError

from apps.portfolio.models import (
    PortfolioProfile,
    Project,
    Resume,
    Skill,
    SkillCategory,
    Technology,
)


@pytest.fixture(autouse=True)
def use_temp_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.mark.django_db
def test_resume_unique_current_constraint_raises_integrity_error():
    file1 = SimpleUploadedFile("resume_current_1.pdf", b"resume content 1")
    file2 = SimpleUploadedFile("resume_current_2.pdf", b"resume content 2")

    Resume.objects.create(
        title="Active Resume v1",
        file=file1,
        is_current=True,
    )

    with pytest.raises(IntegrityError):
        Resume.objects.create(
            title="Active Resume v2",
            file=file2,
            is_current=True,
        )


@pytest.mark.django_db
def test_portfolio_profile_singleton_constraint_raises_integrity_error():
    PortfolioProfile.objects.create(
        full_name_en="First Profile",
        full_name_fa="پروفایل اول",
        headline_en="Lead Engineer",
        headline_fa="مهندس ارشد",
        bio_en="Bio 1",
        bio_fa="بیوگرافی ۱",
        github_url="https://github.com/one",
        linkedin_url="https://linkedin.com/in/one",
        email="one@example.com",
    )

    with pytest.raises(IntegrityError):
        PortfolioProfile.objects.create(
            full_name_en="Second Profile",
            full_name_fa="پروفایل دوم",
            headline_en="Another Lead",
            headline_fa="مهندس دیگر",
            bio_en="Bio 2",
            bio_fa="بیوگرافی ۲",
            github_url="https://github.com/two",
            linkedin_url="https://linkedin.com/in/two",
            email="two@example.com",
        )


@pytest.mark.django_db
def test_skill_category_protected_on_delete_with_skills():
    category = SkillCategory.objects.create(
        name_en="Infrastructure",
        name_fa="زیرساخت",
    )
    Skill.objects.create(
        name_en="Kubernetes",
        name_fa="کوبرنتیز",
        category=category,
    )

    with pytest.raises(ProtectedError):
        category.delete()


@pytest.mark.django_db
def test_project_unique_slug_constraint():
    Project.objects.create(
        title_en="Slug Test 1",
        title_fa="تست اسلاگ ۱",
        slug="unique-project-slug",
        description_en="Desc 1",
        description_fa="توضیحات ۱",
    )

    with pytest.raises(IntegrityError):
        Project.objects.create(
            title_en="Slug Test 2",
            title_fa="تست اسلاگ ۲",
            slug="unique-project-slug",
            description_en="Desc 2",
            description_fa="توضیحات ۲",
        )


@pytest.mark.django_db
def test_technology_unique_slug_constraint():
    Technology.objects.create(
        name="Redis",
        slug="redis",
    )

    with pytest.raises(IntegrityError):
        Technology.objects.create(
            name="Redis Duplicate",
            slug="redis",
        )
