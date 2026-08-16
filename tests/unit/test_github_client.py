import httpx
import pytest

from integrations.github.client import GitHubClient
from integrations.github.exceptions import (
    GitHubAPIError,
    GitHubNetworkError,
    GitHubRateLimitError,
)


def test_client_headers_contain_token():
    client = GitHubClient(token="ghp_mock_token_secret")
    headers = client._build_headers()

    assert headers["Authorization"] == "Bearer ghp_mock_token_secret"
    assert "application/vnd.github.v3+json" in headers["Accept"]


def test_execute_rest_success(monkeypatch):
    def mock_send(self, request, **kwargs):
        return httpx.Response(
            status_code=200,
            json={"login": "testdev", "public_repos": 20},
            request=request,
        )

    monkeypatch.setattr(httpx.Client, "send", mock_send)

    client = GitHubClient()
    result = client.execute_rest("/users/testdev")

    assert result["login"] == "testdev"
    assert result["public_repos"] == 20


def test_timeout_raises_github_network_error(monkeypatch):
    def mock_send(self, request, **kwargs):
        raise httpx.ReadTimeout("Read operation timed out", request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)

    client = GitHubClient()
    with pytest.raises(GitHubNetworkError) as exc_info:
        client.execute_rest("/users/testdev")

    assert "Network error" in str(exc_info.value)


def test_rate_limit_raises_github_rate_limit_error(monkeypatch):
    def mock_send(self, request, **kwargs):
        return httpx.Response(
            status_code=403,
            text='{"message": "API rate limit exceeded"}',
            request=request,
        )

    monkeypatch.setattr(httpx.Client, "send", mock_send)

    client = GitHubClient()
    with pytest.raises(GitHubRateLimitError):
        client.execute_rest("/users/testdev")


def test_graphql_error_response_raises_api_error(monkeypatch):
    def mock_send(self, request, **kwargs):
        return httpx.Response(
            status_code=200,
            json={"errors": [{"message": "Field 'unknown' is invalid"}]},
            request=request,
        )

    monkeypatch.setattr(httpx.Client, "send", mock_send)

    client = GitHubClient()
    with pytest.raises(GitHubAPIError) as exc_info:
        client.execute_graphql(query="query { unknown }")

    assert "Field 'unknown' is invalid" in str(exc_info.value)
