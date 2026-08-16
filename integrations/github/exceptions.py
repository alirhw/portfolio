class GitHubIntegrationError(Exception):
    """Base exception for GitHub integration operations."""


class GitHubNetworkError(GitHubIntegrationError):
    """Raised when a network transport error, DNS resolution failure, or timeout occurs."""


class GitHubAPIError(GitHubIntegrationError):
    """Raised when GitHub API returns an unsuccessful HTTP response (>= 400)."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"GitHub API returned HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message


class GitHubRateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit quota is exceeded."""
