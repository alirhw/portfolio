import os

from .base import *  # noqa: F403

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

DEBUG = False

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-test-key",
)

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "portfolio-test",
    }
}
