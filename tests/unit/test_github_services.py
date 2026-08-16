from unittest.mock import MagicMock

import pytest
from django.core.cache import cache

from integrations.github.exceptions import GitHubNetworkError
from integrations.github.schemas import NormalizedGitHubMetrics
from integrations.github.services import GitHubStatsService


@pytest.fixture(autouse=True)
def clean_cache():
    cache.clear()
    yield
    cache.clear()


def test_get_stats_fetches_and_sets_cache():
    mock_client = MagicMock()
    mock_client.execute_graphql.return_value = {
        "data": {
            "user": {
                "followers": {"totalCount": 25},
                "repositories": {"totalCount": 10, "nodes": []},
                "contributionsCollection": {
                    "contributionCalendar": {"totalContributions": 180, "weeks": []}
                },
            }
        }
    }

    service = GitHubStatsService(client=mock_client, username="developer")
    result = service.get_stats()

    assert result.username == "developer"
    assert result.total_contributions == 180
    assert not result.is_stale

    # Verify data is stored in cache
    cached = cache.get(GitHubStatsService.CACHE_KEY)
    assert cached is not None
    assert cached.total_contributions == 180

    # Subsequent invocation should return from cache without network calls
    second_result = service.get_stats()
    assert second_result.total_contributions == 180
    assert mock_client.execute_graphql.call_count == 1


def test_get_stats_returns_cached_data_when_api_fails():
    # Store valid metrics in cache
    initial_metrics = NormalizedGitHubMetrics(
        username="developer",
        total_contributions=95,
        public_repos_count=3,
        total_stars_earned=5,
        current_streak_days=2,
        followers_count=10,
        top_languages=[],
        is_stale=False,
    )
    cache.set(GitHubStatsService.CACHE_KEY, initial_metrics, 3600)

    # Simulate network error on subsequent API call
    mock_client = MagicMock()
    mock_client.execute_graphql.side_effect = GitHubNetworkError("Connection timed out")

    service = GitHubStatsService(client=mock_client, username="developer")
    result = service.get_stats()

    # Must return cached data
    assert result.total_contributions == 95


def test_get_stats_returns_neutral_fallback_when_no_cache_and_api_fails():
    mock_client = MagicMock()
    mock_client.execute_graphql.side_effect = GitHubNetworkError("Server down")

    service = GitHubStatsService(client=mock_client, username="developer")
    result = service.get_stats()

    # When cache is empty and API fails, must return safe fallback without crashing
    assert result.username == "developer"
    assert result.total_contributions == 0
    assert result.is_stale is True


def test_service_returns_empty_when_no_username_configured():
    service = GitHubStatsService(username="")
    metrics = service.get_stats()

    assert metrics.username == ""
    assert metrics.is_stale is True


def test_get_metrics_alias_with_force_refresh():
    mock_client = MagicMock()
    mock_client.execute_graphql.return_value = {
        "data": {
            "user": {
                "followers": {"totalCount": 50},
                "repositories": {"totalCount": 20, "nodes": []},
                "contributionsCollection": {
                    "contributionCalendar": {"totalContributions": 300, "weeks": []}
                },
            }
        }
    }

    service = GitHubStatsService(client=mock_client, username="developer")
    metrics = service.get_metrics()
    assert metrics.total_contributions == 300
    assert mock_client.execute_graphql.call_count == 1

    # Force refresh must bypass cache and re-query
    refreshed_metrics = service.get_metrics(force_refresh=True)
    assert refreshed_metrics.total_contributions == 300
    assert mock_client.execute_graphql.call_count == 2
