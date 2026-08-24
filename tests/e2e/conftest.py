import os
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from apps.portfolio.models import (
    Education,
    Experience,
    PortfolioProfile,
    Project,
    Skill,
    SkillCategory,
    Technology,
)
from integrations.github.schemas import NormalizedGitHubMetrics

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    chrome_path = (
        Path.home()
        / "AppData"
        / "Local"
        / "ms-playwright"
        / "chromium-1234"
        / "chrome-win64"
        / "chrome.exe"
    )
    if chrome_path.exists():
        return {
            **browser_type_launch_args,
            "executable_path": str(chrome_path),
        }
    return browser_type_launch_args


@pytest.fixture(autouse=True)
def mock_e2e_github_stats():
    """Mock GitHub stats service during E2E tests to avoid external network latency."""
    fake_stats = NormalizedGitHubMetrics(
        username="default-user",
        total_contributions=450,
        public_repos_count=24,
        total_stars_earned=88,
        current_streak_days=14,
        followers_count=10,
    )
    with patch("apps.portfolio.views.GitHubStatsService.get_stats", return_value=fake_stats):
        yield


@pytest.fixture
def seed_e2e_data(db):
    profile = PortfolioProfile.objects.create(
        full_name_en="Ali Developer",
        full_name_fa="علی برنامه‌نویس",
        headline_en="Senior Backend Engineer",
        headline_fa="مهندس ارشد بک‌اند",
        bio_en="Designing scalable web architectures",
        bio_fa="طراحی معماری‌های وب مقیاس‌پذیر",
        email="contact@ali.dev",
        github_url="https://github.com/alidev",
        linkedin_url="https://linkedin.com/in/alidev",
        available_for_hire=True,
    )

    cat = SkillCategory.objects.create(name_en="Backend", name_fa="بک‌اند")
    Skill.objects.create(name_en="Python", name_fa="پایتون", category=cat, highlight=True)
    Skill.objects.create(name_en="Django", name_fa="جنگو", category=cat, highlight=True)

    tech = Technology.objects.create(name="Python", slug="python")
    project = Project.objects.create(
        title_en="Distributed Engine",
        title_fa="موتور توزیع‌شده",
        slug="distributed-engine",
        description_en="High-performance task queue",
        description_fa="صف وظایف با کارایی بالا",
        is_published=True,
    )
    project.technologies.add(tech)

    Experience.objects.create(
        position_en="Lead Architect",
        position_fa="معمار ارشد",
        company="Core Systems",
        start_date=date(2023, 1, 1),
    )
    Education.objects.create(
        degree_en="B.Sc.",
        degree_fa="کارشناسی",
        field_of_study_en="Computer Science",
        field_of_study_fa="علوم کامپیوتر",
        institution_en="University",
        institution_fa="دانشگاه",
        start_year=2018,
        graduation_year=2022,
    )

    return profile
