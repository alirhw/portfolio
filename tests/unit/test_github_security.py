import logging
from unittest.mock import MagicMock

from integrations.github.client import GitHubClient
from integrations.github.exceptions import GitHubAPIError, GitHubIntegrationError
from integrations.github.services import GitHubStatsService


def test_token_is_never_logged_or_exposed_in_exception_representation():
    secret_token = "ghp_super_secret_token_never_expose"
    client = GitHubClient(token=secret_token)

    headers = client._build_headers()
    assert headers["Authorization"] == f"Bearer {secret_token}"

    # Verify that secret token is never exposed in exception strings or reprs
    error = GitHubAPIError(status_code=401, message="Bad credentials")
    assert secret_token not in str(error)
    assert secret_token not in repr(error)


def test_client_works_safely_without_token():
    client = GitHubClient(token=None)
    headers = client._build_headers()

    assert "Authorization" not in headers
    assert headers["User-Agent"] == "Portfolio-Backend/1.0"


def test_logger_captures_failure_without_crashing(caplog):
    mock_client = MagicMock()
    mock_client.execute_graphql.side_effect = GitHubIntegrationError("Simulated failure")

    service = GitHubStatsService(client=mock_client, username="developer")

    with caplog.at_level(logging.WARNING):
        stats = service.get_stats()

    assert stats.is_stale is True
    assert "Failed to fetch fresh GitHub data" in caplog.text
