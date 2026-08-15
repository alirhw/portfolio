import pytest
from django.db import IntegrityError

from apps.portfolio.models import PortfolioProfile


@pytest.mark.django_db
def test_portfolio_profile_can_be_created():
    profile = PortfolioProfile.objects.create(
        full_name_en="Ali",
        full_name_fa="علی",
        headline_en="Backend Developer",
        headline_fa="توسعه‌دهنده بک‌اند",
        bio_en="Backend developer.",
        bio_fa="توسعه‌دهنده بک‌اند.",
        github_url="https://github.com/example",
        linkedin_url="https://www.linkedin.com/in/example",
        email="ali@example.com",
    )

    assert profile.pk is not None
    assert profile.available_for_hire is True
    assert str(profile) == "Ali"


@pytest.mark.django_db
def test_portfolio_profile_is_singleton():
    PortfolioProfile.objects.create(
        full_name_en="Ali",
        full_name_fa="علی",
        headline_en="Backend Developer",
        headline_fa="توسعه‌دهنده بک‌اند",
        bio_en="Backend developer.",
        bio_fa="توسعه‌دهنده بک‌اند.",
        github_url="https://github.com/example",
        linkedin_url="https://www.linkedin.com/in/example",
        email="ali@example.com",
    )

    with pytest.raises(IntegrityError):
        PortfolioProfile.objects.create(
            full_name_en="Another",
            full_name_fa="شخص دیگر",
            headline_en="Developer",
            headline_fa="برنامه‌نویس",
            bio_en="Test",
            bio_fa="تست",
            github_url="https://github.com/example2",
            linkedin_url="https://www.linkedin.com/in/example2",
            email="other@example.com",
        )
