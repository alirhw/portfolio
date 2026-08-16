from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LanguageMetric:
    name: str
    color: str
    percentage: float


@dataclass(frozen=True)
class GitHubMetrics:
    total_contributions: int = 0
    public_repos_count: int = 0
    total_stars_earned: int = 0
    current_streak_days: int = 0
    followers_count: int = 0
    top_languages: list[LanguageMetric] = field(default_factory=list)
    is_stale: bool = False

    @classmethod
    def empty(cls) -> GitHubMetrics:
        """
        مقدار پیش‌فرض و امن (Safe Fallback) هنگام قطعی یا در دسترس نبودن GitHub API
        """
        return cls(
            total_contributions=0,
            public_repos_count=0,
            total_stars_earned=0,
            current_streak_days=0,
            followers_count=0,
            top_languages=[],
            is_stale=True,
        )
