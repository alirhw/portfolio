import httpx
import pytest
from django.core.cache import cache

from integrations.github.client import GitHubClient
from integrations.github.exceptions import (
    GitHubAPIError,
    GitHubNetworkError,
    GitHubRateLimitError,
)
from integrations.github.schemas import NormalizedGitHubMetrics
from integrations.github.services import GitHubStatsService


@pytest.fixture(autouse=True)
def flush_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.parametrize(
    ("status_code", "response_text", "expected_exception"),
    [
        (401, '{"message": "Bad credentials"}', GitHubAPIError),
        (403, '{"message": "API rate limit exceeded"}', GitHubRateLimitError),
        (404, '{"message": "Not Found"}', GitHubAPIError),
        (500, "Internal Server Error", GitHubAPIError),
        (502, "Bad Gateway", GitHubAPIError),
        (503, "Service Unavailable", GitHubAPIError),
    ],
)
def test_github_client_http_error_responses(
    monkeypatch, status_code, response_text, expected_exception
):
    def mock_send(self, request, **kwargs):
        return httpx.Response(
            status_code=status_code,
            text=response_text,
            request=request,
        )

    monkeypatch.setattr(httpx.Client, "send", mock_send)

    client = GitHubClient(token="dummy")
    with pytest.raises(expected_exception):
        client.execute_graphql("query { viewer { login } }")


def test_github_client_handles_network_timeouts(monkeypatch):
    def mock_send(self, request, **kwargs):
        raise httpx.ConnectTimeout("Connection timed out after 1.5s", request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)

    client = GitHubClient()
    with pytest.raises(GitHubNetworkError) as exc_info:
        client.execute_rest("/users/dummy")

    assert "Network error" in str(exc_info.value)


def test_service_resilience_matrix_never_raises_uncaught_exception(monkeypatch):
    """
    Ensure Graceful Degradation never leaks unhandled exceptions when network fails.
    """

    def mock_send_failing(self, request, **kwargs):
        raise httpx.ReadTimeout("Socket read timeout", request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send_failing)

    service = GitHubStatsService(username="developer")

    # get_stats must never raise unhandled exceptions
    metrics = service.get_stats()
    assert isinstance(metrics, NormalizedGitHubMetrics)
    assert metrics.is_stale is True
    assert metrics.total_contributions == 0
