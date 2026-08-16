from integrations.github.normalizers import GitHubDataNormalizer
from integrations.github.schemas import NormalizedGitHubMetrics


def test_normalizer_processes_valid_graphql_response():
    raw_payload = {
        "data": {
            "user": {
                "name": "Ali Developer",
                "followers": {"totalCount": 42},
                "repositories": {
                    "totalCount": 5,
                    "nodes": [
                        {
                            "name": "Repo1",
                            "stargazerCount": 10,
                            "languages": {
                                "edges": [
                                    {"size": 8000, "node": {"name": "Python", "color": "#3572A5"}},
                                    {"size": 2000, "node": {"name": "HTML", "color": "#e34c26"}},
                                ]
                            },
                        },
                        {
                            "name": "Repo2",
                            "stargazerCount": 15,
                            "languages": {
                                "edges": [
                                    {"size": 10000, "node": {"name": "Python", "color": "#3572A5"}},
                                ]
                            },
                        },
                    ],
                },
                "contributionsCollection": {
                    "contributionCalendar": {
                        "totalContributions": 350,
                        "weeks": [
                            {
                                "contributionDays": [
                                    {"contributionCount": 2, "date": "2026-08-14"},
                                    {"contributionCount": 5, "date": "2026-08-15"},
                                    {"contributionCount": 1, "date": "2026-08-16"},
                                ]
                            }
                        ],
                    }
                },
            }
        }
    }

    metrics = GitHubDataNormalizer.normalize_metrics(raw_payload, username="alidev")

    assert isinstance(metrics, NormalizedGitHubMetrics)
    assert metrics.username == "alidev"
    assert metrics.followers_count == 42
    assert metrics.public_repos_count == 5
    assert metrics.total_stars_earned == 25
    assert metrics.total_contributions == 350
    assert metrics.current_streak_days == 3
    assert not metrics.is_stale

    # Verify top languages calculation and breakdown
    assert len(metrics.top_languages) == 2
    assert metrics.top_languages[0].name == "Python"
    assert metrics.top_languages[0].percentage == 90.0
    assert metrics.top_languages[1].name == "HTML"
    assert metrics.top_languages[1].percentage == 10.0


def test_normalizer_handles_empty_or_malformed_payload():
    empty_payload = {}
    metrics = GitHubDataNormalizer.normalize_metrics(empty_payload, username="unknown")

    assert metrics.username == "unknown"
    assert metrics.total_contributions == 0
    assert metrics.total_stars_earned == 0
    assert metrics.top_languages == []
    assert metrics.is_stale is True
