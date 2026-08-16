class GitHubIntegrationError(Exception):
    """خطای پایه برای ارتباطات یکپارچه‌سازی گیت‌هاب."""


class GitHubNetworkError(GitHubIntegrationError):
    """خطای اتصال فیزیکی شبکه، قطعی DNS یا Timeout."""


class GitHubAPIError(GitHubIntegrationError):
    """خطای پاسخ غیرموفق HTTP از سمت گیت‌هاب."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"GitHub API returned HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message


class GitHubRateLimitError(GitHubAPIError):
    """اتمام سهمیه مجاز فراخوانی API (Rate Limit Exceeded)."""
