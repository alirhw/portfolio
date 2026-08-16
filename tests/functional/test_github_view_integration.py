from unittest.mock import patch

import pytest
from django.urls import reverse

from integrations.github.schemas import LanguageBreakdown, NormalizedGitHubMetrics


@pytest.mark.django_db
def test_homepage_renders_with_mocked_github_stats_successfully(client):
    mock_metrics = NormalizedGitHubMetrics(
        username="alidev",
        total_contributions=450,
        public_repos_count=12,
        total_stars_earned=88,
        current_streak_days=10,
        followers_count=35,
        top_languages=[
            LanguageBreakdown(name="Python", color="#3572A5", percentage=80.0, bytes_count=8000),
            LanguageBreakdown(
                name="JavaScript", color="#f1e05a", percentage=20.0, bytes_count=2000
            ),
        ],
        is_stale=False,
    )

    with patch(
        "integrations.github.services.GitHubStatsService.get_stats", return_value=mock_metrics
    ):
        response = client.get(reverse("portfolio:home"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_homepage_does_not_crash_when_github_service_returns_stale_data(client):
    stale_metrics = NormalizedGitHubMetrics.empty(username="alidev")

    with patch(
        "integrations.github.services.GitHubStatsService.get_stats", return_value=stale_metrics
    ):
        response = client.get(reverse("portfolio:home"))

    # Homepage must return 200 even when GitHub service returns empty/stale data
    assert response.status_code == 200
