from config.settings.production import sanitize_sentry_events


def test_sanitize_sentry_events_filters_sensitive_env_keys():
    """Verify sanitize_sentry_events scrubs credentials and sensitive keys."""
    dummy_event = {
        "request": {
            "env": {
                "SECRET_KEY": "super-secret-django-key",
                "DATABASE_URL": "postgresql://user:pass@host/db",
                "GITHUB_ACCESS_TOKEN": "ghp_1234567890abcdef",
                "PUBLIC_VARIABLE": "visible-value",
            },
            "data": {
                "sender_name": "Valid User",
                "password": "my_plain_password",
                "csrfmiddlewaretoken": "token123",
            },
        }
    }

    sanitized = sanitize_sentry_events(dummy_event, hint=None)

    env = sanitized["request"]["env"]
    data = sanitized["request"]["data"]

    # Verify sensitive environment keys are filtered
    assert env["SECRET_KEY"] == "[FILTERED]"
    assert env["DATABASE_URL"] == "[FILTERED]"
    assert env["GITHUB_ACCESS_TOKEN"] == "[FILTERED]"
    assert env["PUBLIC_VARIABLE"] == "visible-value"

    # Verify sensitive request form data is filtered
    assert data["password"] == "[FILTERED]"
    assert data["csrfmiddlewaretoken"] == "[FILTERED]"
    assert data["sender_name"] == "Valid User"


def test_sanitize_sentry_events_handles_empty_event():
    """Verify sanitize_sentry_events cleanly handles events without request data."""
    empty_event = {"level": "info", "message": "Standard log"}
    sanitized = sanitize_sentry_events(empty_event, hint=None)
    assert sanitized == empty_event
