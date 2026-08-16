from unittest.mock import MagicMock

import httpx

from apps.contact.forms import ContactForm
from apps.contact.services.turnstile import TurnstileVerificationService


def test_turnstile_service_successful_verification(monkeypatch):
    def fake_post(self, url, *args, **kwargs):
        return httpx.Response(200, json={"success": True})

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    service = TurnstileVerificationService(secret_key="secret-key-123")
    is_valid = service.verify("valid-token-xyz", remote_ip="192.168.1.1")
    assert is_valid is True


def test_turnstile_service_failed_verification(monkeypatch):
    def fake_post(self, url, *args, **kwargs):
        return httpx.Response(
            200,
            json={"success": False, "error-codes": ["invalid-input-response"]},
        )

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    service = TurnstileVerificationService(secret_key="secret-key-123")
    is_valid = service.verify("invalid-token")
    assert is_valid is False


def test_turnstile_service_timeout_handling(monkeypatch):
    def fake_post(self, url, *args, **kwargs):
        raise httpx.ReadTimeout("Timeout")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    service = TurnstileVerificationService(secret_key="secret-key-123")
    is_valid = service.verify("token")
    assert is_valid is False


def test_contact_form_blocks_honeypot_regardless_of_turnstile():
    mock_turnstile = MagicMock()
    mock_turnstile.secret_key = "secret"
    mock_turnstile.verify.return_value = True

    form_data = {
        "sender_name": "Spammer",
        "email": "spam@test.com",
        "message": "Valid length message here",
        "website": "http://bot.site",
        "cf-turnstile-response": "token",
    }

    form = ContactForm(data=form_data, turnstile_service=mock_turnstile)
    assert not form.is_valid()
    assert "website" in form.errors
    # Honeypot stops external Turnstile API call
    assert mock_turnstile.verify.call_count == 0


def test_contact_form_fails_when_turnstile_rejects():
    mock_turnstile = MagicMock()
    mock_turnstile.secret_key = "secret"
    mock_turnstile.verify.return_value = False

    form_data = {
        "sender_name": "Valid User",
        "email": "user@test.com",
        "message": "Legitimate inquiry message here",
        "website": "",
        "cf-turnstile-response": "bad-token",
    }

    form = ContactForm(data=form_data, turnstile_service=mock_turnstile)
    assert not form.is_valid()
    assert "__all__" in form.errors
