"""
Production settings for security hardening and final deployment (Phase 11 - T-054).
"""

import os

from .base import *  # noqa: F403

DEBUG = False

# Allowed hosts in production (injected via environment variable)
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "ali.dev,www.ali.dev").split(",")
    if host.strip()
]

# Production secret key (strictly injected via DJANGO_SECRET_KEY in production)
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "production-secret-key-placeholder-must-be-provided-via-env-vars-at-least-50-characters",
)

# ==============================================================================
# SSL / HTTPS Configuration & Redirects
# ==============================================================================
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ==============================================================================
# Cookies Hardening
# ==============================================================================
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host]

# ==============================================================================
# HTTP Strict Transport Security (HSTS)
# ==============================================================================
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ==============================================================================
# Browser Security Headers
# ==============================================================================
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
