import datetime

import pytest

from apps.portfolio.models import CurrentlyBuilding, Education, Experience


@pytest.mark.django_db
def test_experience_creation_and_current_status():
    exp = Experience.objects.create(
        position_en="Senior Python Engineer",
        position_fa="مهندس ارشد پایتون",
        company="Tech Corp",
        company_url="https://techcorp.example.com",
        start_date=datetime.date(2023, 1, 1),
        is_current=True,
        end_date=None,
        description_en="Developing core backend systems.",
        description_fa="توسعه سیستم‌های هسته بک‌اند.",
    )

    assert exp.pk is not None
    assert exp.is_current is True
    assert exp.end_date is None
    assert str(exp) == "Senior Python Engineer at Tech Corp"


@pytest.mark.django_db
def test_experience_past_with_end_date():
    exp = Experience.objects.create(
        position_en="Django Developer",
        position_fa="برنامه‌نویس جنگو",
        company="Old Startup",
        start_date=datetime.date(2021, 1, 1),
        end_date=datetime.date(2022, 12, 31),
        is_current=False,
    )

    assert exp.end_date == datetime.date(2022, 12, 31)
    assert exp.is_current is False


@pytest.mark.django_db
def test_education_creation_with_bilingual_fields():
    edu = Education.objects.create(
        degree_en="B.Sc. in Software Engineering",
        degree_fa="کارشناسی مهندسی نرم‌افزار",
        institution_en="Tehran University",
        institution_fa="دانشگاه تهران",
        field_of_study_en="Computer Science",
        field_of_study_fa="علوم کامپیوتر",
        start_year=2018,
        graduation_year=2022,
        description_en="Focus on distributed systems and algorithms.",
        description_fa="تمرکز روی سیستم‌های توزیع‌شده و الگوریتم‌ها.",
    )

    assert edu.pk is not None
    assert edu.graduation_year == 2022
    assert str(edu) == "B.Sc. in Software Engineering - Tehran University"


@pytest.mark.django_db
def test_currently_building_creation_with_progress():
    cb = CurrentlyBuilding.objects.create(
        title_en="Portfolio Platform",
        title_fa="پلتفرم پورتفولیو",
        description_en="A modern bilingual developer portfolio.",
        description_fa="پورتفولیوی مدرن و دوزبانه توسعه‌دهنده.",
        progress_percentage=75,
        current_phase_en="Phase 3 — Database Foundation",
        current_phase_fa="فاز ۳ — پایه‌های دیتابیس",
        related_link="https://github.com/example/portfolio",
        is_active=True,
    )

    assert cb.pk is not None
    assert cb.progress_percentage == 75
    assert cb.is_active is True
    assert str(cb) == "Portfolio Platform"
