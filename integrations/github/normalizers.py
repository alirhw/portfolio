from __future__ import annotations

from typing import Any

from .schemas import LanguageBreakdown, NormalizedGitHubMetrics


class GitHubDataNormalizer:
    @staticmethod
    def calculate_current_streak(weeks: list[dict[str, Any]]) -> int:
        """
        Calculate active consecutive contribution days (streak) backwards from the latest day.
        """
        days = []
        for week in weeks:
            for day in week.get("contributionDays", []):
                days.append(day)

        if not days:
            return 0

        streak = 0
        # Traverse days in reverse from the most recent day
        for day in reversed(days):
            if day.get("contributionCount", 0) > 0:
                streak += 1
            else:
                # If current day has 0 contributions yet, do not break streak immediately
                if streak == 0:
                    continue
                break
        return streak

    @staticmethod
    def extract_top_languages(
        repos_nodes: list[dict[str, Any]], limit: int = 4
    ) -> list[LanguageBreakdown]:
        """
        Aggregate bytes for each language across all repositories and compute percentage share.
        """
        lang_totals: dict[str, dict[str, Any]] = {}
        total_bytes_all = 0

        for repo in repos_nodes:
            languages = repo.get("languages", {}).get("edges", [])
            for edge in languages:
                size = edge.get("size", 0)
                node = edge.get("node", {})
                name = node.get("name", "Unknown")
                color = node.get("color") or "#858585"

                total_bytes_all += size
                if name not in lang_totals:
                    lang_totals[name] = {"bytes": 0, "color": color}
                lang_totals[name]["bytes"] += size

        if total_bytes_all == 0:
            return []

        sorted_langs = sorted(
            lang_totals.items(),
            key=lambda item: item[1]["bytes"],
            reverse=True,
        )[:limit]

        result = []
        for name, data in sorted_langs:
            percentage = round((data["bytes"] / total_bytes_all) * 100, 1)
            result.append(
                LanguageBreakdown(
                    name=name,
                    color=data["color"],
                    percentage=percentage,
                    bytes_count=data["bytes"],
                )
            )
        return result

    @classmethod
    def normalize_metrics(cls, raw_data: dict[str, Any], username: str) -> NormalizedGitHubMetrics:
        """
        Transform raw GraphQL response payload into standard NormalizedGitHubMetrics.
        """
        user_data = raw_data.get("data", {}).get("user")
        if not user_data:
            return NormalizedGitHubMetrics.empty(username=username)

        followers_count = user_data.get("followers", {}).get("totalCount", 0)

        repos_data = user_data.get("repositories", {})
        public_repos_count = repos_data.get("totalCount", 0)
        repo_nodes = repos_data.get("nodes", [])

        # Sum total stars across user repositories
        total_stars = sum(repo.get("stargazerCount", 0) for repo in repo_nodes)

        # Extract top languages
        top_languages = cls.extract_top_languages(repo_nodes)

        # Process contribution calendar
        calendar = user_data.get("contributionsCollection", {}).get("contributionCalendar", {})
        total_contributions = calendar.get("totalContributions", 0)
        weeks = calendar.get("weeks", [])
        current_streak = cls.calculate_current_streak(weeks)

        return NormalizedGitHubMetrics(
            username=username,
            total_contributions=total_contributions,
            public_repos_count=public_repos_count,
            total_stars_earned=total_stars,
            current_streak_days=current_streak,
            followers_count=followers_count,
            top_languages=top_languages,
            is_stale=False,
        )
