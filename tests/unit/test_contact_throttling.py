import pytest
from django.core.cache import cache

from apps.contact.forms import ContactForm
from apps.contact.services.throttling import is_rate_limited
from apps.contact.utils import get_client_ip


@pytest.fixture(autouse=True)
def flush_cache():
    cache.clear()
    yield
    cache.clear()


def test_is_rate_limited_increments_and_blocks():
    ip = "203.0.113.195"

    # Submissions 1, 2, and 3 must succeed
    assert is_rate_limited(ip, limit=3, timeout=300) is False
    assert is_rate_limited(ip, limit=3, timeout=300) is False
    assert is_rate_limited(ip, limit=3, timeout=300) is False

    # 4th submission is throttled
    assert is_rate_limited(ip, limit=3, timeout=300) is True


def test_is_rate_limited_isolated_per_ip():
    ip1 = "198.51.100.1"
    ip2 = "198.51.100.2"

    for _ in range(3):
        is_rate_limited(ip1, limit=3, timeout=300)

    # First IP is blocked, second IP remains allowed
    assert is_rate_limited(ip1, limit=3, timeout=300) is True
    assert is_rate_limited(ip2, limit=3, timeout=300) is False


def test_get_client_ip_handles_direct_and_forwarded_headers(rf):
    # Direct request
    req_direct = rf.get("/", REMOTE_ADDR="192.0.2.1")
    assert get_client_ip(req_direct) == "192.0.2.1"

    # Proxied request (e.g. Cloudflare / Nginx)
    req_proxied = rf.get(
        "/",
        HTTP_X_FORWARDED_FOR="198.51.100.25, 10.0.0.1",
        REMOTE_ADDR="127.0.0.1",
    )
    assert get_client_ip(req_proxied) == "198.51.100.25"


def test_contact_form_raises_validation_error_when_throttled():
    ip = "192.0.2.100"

    # Fill rate limit quota
    for _ in range(3):
        is_rate_limited(ip, limit=3, timeout=300)

    form_data = {
        "sender_name": "Rapid Sender",
        "email": "user@example.com",
        "message": "Sending repeated requests rapidly.",
        "website": "",
    }

    form = ContactForm(data=form_data, remote_ip=ip)
    assert not form.is_valid()
    assert "__all__" in form.errors
    assert "Too many messages" in str(form.errors["__all__"])
