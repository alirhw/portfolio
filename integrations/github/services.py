from __future__ import annotations

import logging

from django.conf import settings
from django.core.cache import cache

from .client import GitHubClient
from .exceptions import GitHubIntegrationError
from .normalizers import GitHubDataNormalizer
from .queries import USER_METRICS_GRAPHQL_QUERY
from .schemas import NormalizedGitHubMetrics

logger = logging.getLogger(__name__)


class GitHubStatsService:
    """
    Orchestration service for fetching, caching, and managing GitHub statistics
    with graceful degradation and safe fallbacks.
    """

    CACHE_KEY = "github_stats_data"
    CACHE_TIMEOUT = getattr(settings, "GITHUB_CACHE_TTL", 3600)  # Default 1 hour

    def __init__(
        self,
        client: GitHubClient | None = None,
        username: str | None = None,
    ) -> None:
        self.client = client or GitHubClient()
        self.username = (
            username if username is not None else getattr(settings, "GITHUB_USERNAME", "")
        )

    def _get_fallback_data(self) -> NormalizedGitHubMetrics:
        """
        Generate neutral default safe fallback data when cache is empty and network errors occur.
        """
        return NormalizedGitHubMetrics.empty(username=self.username)

    def _fetch_from_api(self) -> NormalizedGitHubMetrics:
        """
        Fetch and normalize statistics directly from the GitHub GraphQL API.
        """
        if not self.username:
            raise GitHubIntegrationError("GitHub username is not configured.")

        raw_response = self.client.execute_graphql(
            query=USER_METRICS_GRAPHQL_QUERY,
            variables={"username": self.username},
        )
        return GitHubDataNormalizer.normalize_metrics(
            raw_data=raw_response,
            username=self.username,
        )

    def get_stats(self) -> NormalizedGitHubMetrics:
        """
        Retrieve GitHub statistics with caching, error handling, and safe fallback.
        """
        cached_data = cache.get(self.CACHE_KEY)
        try:
            # Fetch fresh data if cache is empty
            if not cached_data:
                fresh_data = self._fetch_from_api()
                cache.set(self.CACHE_KEY, fresh_data, self.CACHE_TIMEOUT)
                return fresh_data
            return cached_data
        except Exception as exc:
            logger.warning(
                "Failed to fetch fresh GitHub data for '%s': %s. Returning fallback.",
                self.username,
                exc,
            )
            # Return cached data or safe default on API/network errors
            return cached_data or self._get_fallback_data()

    def get_metrics(self, force_refresh: bool = False) -> NormalizedGitHubMetrics:
        """
        Alias for get_stats with optional force_refresh support.
        """
        if force_refresh:
            cache.delete(self.CACHE_KEY)
        return self.get_stats()
