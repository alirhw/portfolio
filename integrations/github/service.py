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

CACHE_TTL_SECONDS = getattr(settings, "GITHUB_CACHE_TTL", 3600)  # Default 1 hour
CACHE_KEY_PREFIX = "github_metrics"


class GitHubStatsService:
    """
    Orchestration service for fetching, caching, and managing GitHub statistics.
    """

    def __init__(
        self,
        client: GitHubClient | None = None,
        username: str | None = None,
    ) -> None:
        self.client = client or GitHubClient()
        self.username = (
            username if username is not None else getattr(settings, "GITHUB_USERNAME", "")
        )

    def _get_cache_key(self, username: str) -> str:
        return f"{CACHE_KEY_PREFIX}:{username.lower()}"

    def get_metrics(self, force_refresh: bool = False) -> NormalizedGitHubMetrics:
        """
        Fetch metrics with cache priority and safe fallback on network errors.
        """
        if not self.username:
            logger.warning("No GitHub username configured.")
            return NormalizedGitHubMetrics.empty(username="")

        cache_key = self._get_cache_key(self.username)

        # 1. Check cache if force_refresh is not requested
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data is not None and isinstance(cached_data, NormalizedGitHubMetrics):
                return cached_data

        # 2. Call API and update cache
        try:
            raw_response = self.client.execute_graphql(
                query=USER_METRICS_GRAPHQL_QUERY,
                variables={"username": self.username},
            )
            metrics = GitHubDataNormalizer.normalize_metrics(
                raw_data=raw_response,
                username=self.username,
            )

            # Store fresh metrics in cache
            cache.set(cache_key, metrics, timeout=CACHE_TTL_SECONDS)
            return metrics

        except GitHubIntegrationError as exc:
            logger.error(
                "Failed to fetch GitHub metrics for %s: %s",
                self.username,
                exc,
                exc_info=True,
            )

            # 3. Graceful Fallback strategy: return stale cached metrics or empty fallback
            stale_cached = cache.get(cache_key)
            if stale_cached and isinstance(stale_cached, NormalizedGitHubMetrics):
                return NormalizedGitHubMetrics(
                    username=stale_cached.username,
                    total_contributions=stale_cached.total_contributions,
                    public_repos_count=stale_cached.public_repos_count,
                    total_stars_earned=stale_cached.total_stars_earned,
                    current_streak_days=stale_cached.current_streak_days,
                    followers_count=stale_cached.followers_count,
                    top_languages=stale_cached.top_languages,
                    is_stale=True,
                )

            return NormalizedGitHubMetrics.empty(username=self.username)
