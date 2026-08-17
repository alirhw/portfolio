import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.portfolio.models import (
    CurrentlyBuilding,
    PortfolioProfile,
    Project,
    Resume,
    Technology,
)


@pytest.mark.django_db
def test_portfolio_profile_str_and_optional_fields():
    profile = PortfolioProfile.objects.create(
        full_name_en="Edge Tester",
        full_name_fa="آزمایشگر لبه",
        headline_en="Software Architect",
        headline_fa="معمار نرم‌افزار",
        bio_en="",
        bio_fa="",
        available_for_hire=False,
    )
    assert "Edge Tester" in str(profile)
    assert profile.is_available is False


@pytest.mark.django_db
def test_project_custom_queryset_published_filtering():
    t1 = Technology.objects.create(name="Go", slug="go")

    p_pub = Project.objects.create(
        title_en="Public Repo",
        title_fa="مخزن عمومی",
        slug="public-repo",
        description_en="Live tool",
        description_fa="ابزار زنده",
        is_published=True,
    )
    p_pub.technologies.add(t1)

    p_draft = Project.objects.create(
        title_en="Draft Repo",
        title_fa="مخزن پیش‌نویس",
        slug="draft-repo",
        description_en="Internal tool",
        description_fa="ابزار داخلی",
        is_published=False,
    )

    published_qs = Project.objects.published()
    assert p_pub in published_qs
    assert p_draft not in published_qs


@pytest.mark.django_db
def test_resume_resolution_picks_current_active():
    pdf = SimpleUploadedFile("r.pdf", b"%PDF-1.4 dummy", content_type="application/pdf")

    _r1 = Resume.objects.create(title="Old Inactive", file=pdf, is_current=False)
    r2 = Resume.objects.create(title="Active Resume", file=pdf, is_current=True)

    # get_current should deterministically resolve to the active resume
    current = Resume.get_current()
    assert current is not None
    assert current.id == r2.id


@pytest.mark.django_db
def test_currently_building_progress_bounds():
    cb = CurrentlyBuilding.objects.create(
        title_en="Edge Exploration",
        title_fa="اکتشاف لبه",
        description_en="Testing boundaries",
        description_fa="آزمون مرزها",
        progress_percentage=100,
        is_active=True,
    )
    assert cb.progress_percentage == 100
    assert cb.is_active is True
