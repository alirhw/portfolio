import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from apps.portfolio.models import Resume


@pytest.fixture(autouse=True)
def use_temp_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.mark.django_db
def test_resume_non_current_can_be_created_multiple_times():
    file1 = SimpleUploadedFile("resume_v1.pdf", b"dummy content 1")
    file2 = SimpleUploadedFile("resume_v2.pdf", b"dummy content 2")

    r1 = Resume.objects.create(
        title="Resume 2024",
        file=file1,
        version="v1.0",
        is_current=False,
    )
    r2 = Resume.objects.create(
        title="Resume 2025",
        file=file2,
        version="v2.0",
        is_current=False,
    )

    assert r1.pk is not None
    assert r2.pk is not None
    assert Resume.objects.filter(is_current=False).count() == 2
    assert str(r1) == "Resume 2024"


@pytest.mark.django_db
def test_single_current_resume_can_be_created():
    current_file = SimpleUploadedFile("resume_current.pdf", b"current resume content")
    resume = Resume.objects.create(
        title="Latest Resume",
        file=current_file,
        version="v3.0",
        is_current=True,
    )

    assert resume.pk is not None
    assert resume.is_current is True
    assert str(resume) == "Latest Resume (Current)"


@pytest.mark.django_db
def test_duplicate_current_resume_raises_integrity_error():
    file1 = SimpleUploadedFile("resume_1.pdf", b"content 1")
    file2 = SimpleUploadedFile("resume_2.pdf", b"content 2")

    Resume.objects.create(
        title="First Current Resume",
        file=file1,
        is_current=True,
    )

    with pytest.raises(IntegrityError):
        Resume.objects.create(
            title="Second Current Resume",
            file=file2,
            is_current=True,
        )


@pytest.mark.django_db
def test_resume_constraint_exists_in_meta():
    constraint_names = [c.name for c in Resume._meta.constraints]
    assert "unique_current_resume" in constraint_names
