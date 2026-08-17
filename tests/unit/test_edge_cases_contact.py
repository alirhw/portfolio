import httpx
import pytest
from django.core.cache import cache

from apps.contact.models import ContactMessage
from apps.contact.services.submission import ContactSubmissionService
from apps.contact.services.throttling import is_rate_limited
from apps.contact.services.turnstile import TurnstileVerificationService


@pytest.fixture(autouse=True)
def clean_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_contact_message_str_representation():
    msg = ContactMessage.objects.create(
        sender_name="Linus",
        email="linus@kernel.org",
        message="Reviewing merge requests.",
    )
    assert "Linus" in str(msg)
    assert "linus@kernel.org" in str(msg)

    # Test setter/getter for name compatibility
    msg.name = "Linus Torvalds"
    assert msg.sender_name == "Linus Torvalds"
    assert msg.name == "Linus Torvalds"


def test_is_rate_limited_handles_empty_ip():
    # Empty inputs must not raise runtime errors and must not throttle
    assert is_rate_limited("") is False
    assert is_rate_limited(None) is False


@pytest.mark.django_db
def test_contact_submission_service_handles_blank_subject():
    msg = ContactSubmissionService.submit_message(
        sender_name="Ada Lovelace",
        email="ada@analytical.org",
        message="First algorithm specification.",
        subject="",  # Optional blank subject
    )
    assert msg.id is not None
    assert msg.subject == ""


@pytest.mark.django_db
def test_contact_submission_service_uses_admins_setting_fallback(settings):
    settings.CONTACT_NOTIFICATION_EMAIL = None
    settings.ADMINS = [("Security", "secops@portfolio.local")]

    msg = ContactSubmissionService.submit_message(
        sender_name="Grace Hopper",
        email="grace@navy.mil",
        message="Compiler architecture discussion.",
    )
    assert msg.id is not None
    assert msg.is_notified is True


def test_turnstile_service_edge_cases(monkeypatch):
    # Case 1: No secret key configured (bypass verification)
    no_key_service = TurnstileVerificationService(secret_key=None)
    assert no_key_service.verify("any-token") is True

    # Case 2: Secret key set but empty token provided
    keyed_service = TurnstileVerificationService(secret_key="secret-123")
    assert keyed_service.verify("") is False

    # Case 3: HTTP 500 status code response
    def fake_500_post(self, url, *args, **kwargs):
        return httpx.Response(500, text="Internal Server Error")

    monkeypatch.setattr(httpx.Client, "post", fake_500_post)
    assert keyed_service.verify("some-token") is False
