import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.portfolio.models import Resume


@pytest.fixture
def fake_pdf():
    return SimpleUploadedFile(
        "resume.pdf",
        b"%PDF-1.4 dummy content",
        content_type="application/pdf",
    )


@pytest.mark.django_db
def test_get_current_returns_active_resume(fake_pdf):
    Resume.objects.create(
        title="Old Resume 2024",
        file=fake_pdf,
        is_current=False,
    )
    active_resume = Resume.objects.create(
        title="Current Resume 2026",
        file=fake_pdf,
        is_current=True,
    )

    resolved_resume = Resume.get_current()
    assert resolved_resume is not None
    assert resolved_resume.id == active_resume.id
    assert resolved_resume.title == "Current Resume 2026"


@pytest.mark.django_db
def test_get_current_returns_none_when_no_active_resume(fake_pdf):
    Resume.objects.create(
        title="Draft Resume",
        file=fake_pdf,
        is_current=False,
    )

    assert Resume.get_current() is None


@pytest.mark.django_db
def test_get_current_returns_none_on_empty_database():
    assert Resume.objects.count() == 0
    assert Resume.get_current() is None
