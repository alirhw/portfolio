from apps.portfolio.services.github_types import GitHubMetrics, LanguageMetric


def test_github_metrics_instantiation():
    lang = LanguageMetric(name="Python", color="#3572A5", percentage=72.5)
    metrics = GitHubMetrics(
        total_contributions=840,
        public_repos_count=18,
        total_stars_earned=145,
        current_streak_days=14,
        followers_count=52,
        top_languages=[lang],
        is_stale=False,
    )

    assert metrics.total_contributions == 840
    assert metrics.public_repos_count == 18
    assert metrics.total_stars_earned == 145
    assert metrics.current_streak_days == 14
    assert metrics.followers_count == 52
    assert len(metrics.top_languages) == 1
    assert metrics.top_languages[0].name == "Python"
    assert metrics.top_languages[0].color == "#3572A5"
    assert metrics.top_languages[0].percentage == 72.5
    assert not metrics.is_stale


def test_github_metrics_empty_fallback():
    fallback = GitHubMetrics.empty()

    assert fallback.total_contributions == 0
    assert fallback.public_repos_count == 0
    assert fallback.total_stars_earned == 0
    assert fallback.current_streak_days == 0
    assert fallback.followers_count == 0
    assert fallback.top_languages == []
    assert fallback.is_stale is True
