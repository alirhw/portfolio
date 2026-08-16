from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LanguageBreakdown:
    name: str
    color: str
    percentage: float
    bytes_count: int


@dataclass(frozen=True)
class NormalizedGitHubMetrics:
    username: str
    total_contributions: int
    public_repos_count: int
    total_stars_earned: int
    current_streak_days: int
    followers_count: int
    top_languages: list[LanguageBreakdown] = field(default_factory=list)
    is_stale: bool = False

    @classmethod
    def empty(cls, username: str = "") -> NormalizedGitHubMetrics:
        """
        Default safe fallback values in case of error or unavailable data.
        """
        return cls(
            username=username,
            total_contributions=0,
            public_repos_count=0,
            total_stars_earned=0,
            current_streak_days=0,
            followers_count=0,
            top_languages=[],
            is_stale=True,
        )
