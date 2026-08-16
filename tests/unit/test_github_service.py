from unittest.mock import MagicMock

import pytest
from django.core.cache import cache

from integrations.github.exceptions import GitHubNetworkError
from integrations.github.service import GitHubStatsService


@pytest.fixture(autouse=True)
def clear_django_cache():
    cache.clear()
    yield
    cache.clear()


def test_service_fetches_and_caches_metrics():
    mock_client = MagicMock()
    mock_client.execute_graphql.return_value = {
        "data": {
            "user": {
                "followers": {"totalCount": 15},
                "repositories": {"totalCount": 8, "nodes": []},
                "contributionsCollection": {
                    "contributionCalendar": {
                        "totalContributions": 120,
                        "weeks": [],
                    }
                },
            }
        }
    }

    service = GitHubStatsService(client=mock_client, username="testuser")
    metrics = service.get_metrics()

    assert metrics.username == "testuser"
    assert metrics.total_contributions == 120
    assert metrics.followers_count == 15
    assert not metrics.is_stale
    assert mock_client.execute_graphql.call_count == 1

    # Second invocation should read directly from cache without hitting network
    cached_metrics = service.get_metrics()
    assert cached_metrics.total_contributions == 120
    assert mock_client.execute_graphql.call_count == 1


def test_service_graceful_fallback_on_network_error():
    mock_client = MagicMock()
    mock_client.execute_graphql.side_effect = GitHubNetworkError("Connection timed out")

    service = GitHubStatsService(client=mock_client, username="testuser")
    metrics = service.get_metrics()

    # Must not crash, should return safe fallback object
    assert metrics.username == "testuser"
    assert metrics.total_contributions == 0
    assert metrics.is_stale is True


def test_service_returns_empty_when_no_username_configured():
    service = GitHubStatsService(username="")
    metrics = service.get_metrics()

    assert metrics.username == ""
    assert metrics.is_stale is True
