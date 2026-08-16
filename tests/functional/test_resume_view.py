import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.portfolio.models import PortfolioProfile, Resume


@pytest.fixture
def active_resume(db):
    pdf_file = SimpleUploadedFile(
        "ali_developer_resume.pdf",
        b"%PDF-1.4 sample binary stream for resume test",
        content_type="application/pdf",
    )
    return Resume.objects.create(
        title="Ali Dev Resume 2026",
        file=pdf_file,
        is_current=True,
    )


@pytest.mark.django_db
def test_resume_download_returns_200_and_correct_headers(client, active_resume):
    url = reverse("portfolio:resume_download")
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert "inline;" in response["Content-Disposition"]
    assert "ali_developer_resume" in response["Content-Disposition"]


@pytest.mark.django_db
def test_resume_download_returns_404_when_no_active_resume(client):
    url = reverse("portfolio:resume_download")
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_resume_link_visible_on_homepage_only_when_active(client, active_resume):
    PortfolioProfile.objects.create(
        full_name_en="Ali Developer",
        full_name_fa="علی توسعه‌دهنده",
        headline_en="Senior Backend Engineer",
        headline_fa="مهندس ارشد بک‌اند",
        bio_en="Designing resilient architectures",
        bio_fa="طراحی معماری‌های تاب‌آور",
    )

    home_url = reverse("portfolio:home")
    response = client.get(home_url)
    assert response.status_code == 200
    html = response.content.decode()

    resume_url = reverse("portfolio:resume_download")
    assert resume_url in html

    # غیرفعال کردن رزومه
    active_resume.is_current = False
    active_resume.save()

    response_after = client.get(home_url)
    assert resume_url not in response_after.content.decode()
