"""
Production settings (Phase 12 - Tasks T-060, T-063, T-068).
PostgreSQL database via DATABASE_URL, Sentry monitoring, structured logging,
WhiteNoise storage, SMTP email delivery, and secret sanitization.
"""

import logging
import os

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .base import *  # noqa: F403

# 1. Environment status
DEBUG = False

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    os.environ.get(
        "DJANGO_SECRET_KEY",
        "production-dummy-secret-key-for-deploy-checks-at-least-50-chars",
    ),
)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        ".railway.app,.up.railway.app,localhost,127.0.0.1,0.0.0.0,portfolio.alirhw.dev",
    ).split(",")
    if host.strip()
]

# 2. Database configuration via DATABASE_URL
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv(
            "DATABASE_URL",
            "sqlite:///" + str(BASE_DIR / "db.sqlite3"),  # noqa: F405
        ),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=os.getenv("DB_SSL_REQUIRE", "False").lower() in ("true", "1", "yes"),
    )
}

# 3. External service integration credentials
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "alirhw")
TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY", "")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")

# 4. Secure email configuration (SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.sendgrid.net")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "Ali Developer <contact@ali.dev>")
CONTACT_NOTIFICATION_EMAIL = os.getenv("CONTACT_NOTIFICATION_EMAIL", "ali@ali.dev")


# 5. Sensitive data sanitization for Sentry reports
def sanitize_sentry_events(event, hint):
    """
    Remove sensitive secrets, tokens, and credentials from Sentry event payloads.
    """
    sensitive_keys = {
        "SECRET_KEY",
        "DATABASE_URL",
        "GITHUB_ACCESS_TOKEN",
        "TURNSTILE_SECRET_KEY",
        "EMAIL_HOST_PASSWORD",
        "password",
        "csrfmiddlewaretoken",
    }

    # Filter environment variables in request env
    if "request" in event and "env" in event["request"]:
        for key in list(event["request"]["env"].keys()):
            if key in sensitive_keys or "SECRET" in key or "TOKEN" in key or "KEY" in key:
                event["request"]["env"][key] = "[FILTERED]"

    # Filter POST form data
    if "request" in event and "data" in event["request"]:
        if isinstance(event["request"]["data"], dict):
            for k in event["request"]["data"].keys():
                if k in sensitive_keys:
                    event["request"]["data"][k] = "[FILTERED]"

    return event


# 6. Sentry Error Tracking & Performance Monitoring
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.2")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        before_send=sanitize_sentry_events,
        send_default_pii=False,
        environment=os.getenv("ENVIRONMENT", "production"),
        release=os.getenv("APP_VERSION", "v1.0.0-rc.1"),
    )

# 7. Static files storage and compression with WhiteNoise
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "apps.core.middleware.ContentSecurityPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

WHITENOISE_MAX_AGE = 31536000


def WHITENOISE_IMMUTABLE_FILE_TEST(path, url):
    return True


# 8. Structured logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] "
                "%(process)d %(thread)d %(message)s"
            ),
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "integrations": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# 9. Security and HTTPS flags
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() in ("true", "1", "yes")
SECURE_REDIRECT_EXEMPT = [r"^healthz/?$"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = [
    f"https://{host.lstrip('.')}"
    for host in ALLOWED_HOSTS
    if host and not host.startswith("0.0.0.0") and not host.startswith("127.0.0.1")
] + [
    "https://*.railway.app",
    "https://*.up.railway.app",
]

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
