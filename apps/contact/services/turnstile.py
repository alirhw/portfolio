import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
TURNSTILE_TIMEOUT = httpx.Timeout(2.5, connect=1.0, read=2.0)


class TurnstileVerificationService:
    """
    Server-side verification service for Cloudflare Turnstile tokens.
    Secret key is read securely from settings / environment variables.
    """

    def __init__(self, secret_key: str | None = None) -> None:
        self.secret_key = secret_key or getattr(settings, "TURNSTILE_SECRET_KEY", None)

    def verify(self, response_token: str, remote_ip: str | None = None) -> bool:
        # If secret key is not set (e.g. local dev / test), bypass verification safely
        if not self.secret_key:
            logger.debug("Turnstile secret key is not set; skipping verification.")
            return True

        if not response_token:
            logger.warning("Empty Turnstile response token received.")
            return False

        payload = {
            "secret": self.secret_key,
            "response": response_token,
        }
        if remote_ip:
            payload["remoteip"] = remote_ip

        try:
            with httpx.Client(timeout=TURNSTILE_TIMEOUT) as client:
                response = client.post(TURNSTILE_VERIFY_URL, data=payload)
                if response.status_code != 200:
                    logger.error("Turnstile API returned HTTP %s", response.status_code)
                    return False

                data = response.json()
                success = bool(data.get("success", False))
                if not success:
                    logger.warning("Turnstile verification failed: %s", data.get("error-codes"))
                return success

        except (httpx.TimeoutException, httpx.RequestError) as exc:
            logger.error("Network error during Turnstile verification: %s", exc)
            return False
