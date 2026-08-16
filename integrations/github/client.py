from __future__ import annotations

from typing import Any

import httpx
from django.conf import settings

from .exceptions import (
    GitHubAPIError,
    GitHubNetworkError,
    GitHubRateLimitError,
)

# Strict timeout boundaries per ARCH-021 (maximum 4.0s total)
DEFAULT_TIMEOUT = httpx.Timeout(
    timeout=4.0,
    connect=1.5,
    read=3.0,
    write=1.5,
    pool=1.0,
)

GITHUB_REST_BASE_URL = "https://api.github.com"
GITHUB_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"


class GitHubClient:
    """
    Server-side client for resilient communication with GitHub REST and GraphQL APIs.
    Complies with ARCH-007, ARCH-008, and ARCH-021.
    """

    def __init__(
        self,
        token: str | None = None,
        timeout: httpx.Timeout | None = None,
    ) -> None:
        # Token is strictly resolved server-side with priority to settings/environment
        self._token = token or getattr(settings, "GITHUB_ACCESS_TOKEN", None)
        self._timeout = timeout or DEFAULT_TIMEOUT

    def _build_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Portfolio-Backend/1.0",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def execute_rest(self, endpoint: str) -> dict[str, Any]:
        """
        Execute a GET request to a GitHub REST endpoint.
        """
        url = f"{GITHUB_REST_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, headers=self._build_headers())
                return self._parse_response(response)
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RequestError) as exc:
            raise GitHubNetworkError(f"Network error during GitHub REST call: {exc}") from exc

    def execute_graphql(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute a POST query to the GitHub GraphQL endpoint.
        """
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    GITHUB_GRAPHQL_ENDPOINT,
                    json=payload,
                    headers=self._build_headers(),
                )
                data = self._parse_response(response)

                if "errors" in data and not data.get("data"):
                    err_msg = "; ".join(
                        err.get("message", "Unknown GraphQL error")
                        for err in data.get("errors", [])
                    )
                    raise GitHubAPIError(status_code=response.status_code, message=err_msg)

                return data
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RequestError) as exc:
            raise GitHubNetworkError(f"Network error during GitHub GraphQL call: {exc}") from exc

    def _parse_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.status_code == 403 and "rate limit" in response.text.lower():
            raise GitHubRateLimitError(status_code=403, message="GitHub rate limit exceeded")

        if response.status_code >= 400:
            raise GitHubAPIError(status_code=response.status_code, message=response.text)

        return response.json()
