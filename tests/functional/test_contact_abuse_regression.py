import pytest
from django.core.cache import cache
from django.urls import reverse

from apps.contact.models import ContactMessage


@pytest.fixture(autouse=True)
def flush_rate_limit_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_successful_submission_persists_and_redirects(client):
    url = reverse("contact:submit")
    initial_count = ContactMessage.objects.count()

    form_data = {
        "sender_name": "Marcus Aurelius",
        "email": "marcus@rome.gov",
        "message": "Interested in building resilient software systems.",
        "website": "",  # Empty honeypot
    }

    response = client.post(
        url,
        data=form_data,
        REMOTE_ADDR="198.51.100.44",
        follow=True,
    )

    # Confirm 200 OK after redirect
    assert response.status_code == 200

    # Ensure exactly one record was persisted
    assert ContactMessage.objects.count() == initial_count + 1

    saved_msg = ContactMessage.objects.filter(email="marcus@rome.gov").first()
    assert saved_msg is not None
    assert saved_msg.sender_name == "Marcus Aurelius"
    assert saved_msg.ip_address == "198.51.100.44"
    assert saved_msg.is_read is False


@pytest.mark.django_db
def test_honeypot_filled_blocks_persistence(client):
    url = reverse("contact:submit")
    initial_count = ContactMessage.objects.count()

    form_data = {
        "sender_name": "Spam Bot 3000",
        "email": "bot@automated-spam.com",
        "message": "Buy cheap backlinks at https://spam.example",
        "website": "https://spam.example",  # Honeypot filled by bot
    }

    response = client.post(
        url,
        data=form_data,
        REMOTE_ADDR="203.0.113.88",
        follow=True,
    )

    assert response.status_code == 200

    # Request rejected and zero database records created
    assert ContactMessage.objects.count() == initial_count
    assert not ContactMessage.objects.filter(email="bot@automated-spam.com").exists()


@pytest.mark.django_db
def test_rate_limiting_throttles_after_threshold(client):
    url = reverse("contact:submit")
    client_ip = "192.0.2.77"

    form_payload = {
        "sender_name": "Repeated Sender",
        "email": "repeat@example.com",
        "message": "Legitimate inquiry sent repeatedly.",
        "website": "",
    }

    # Submissions 1, 2, and 3 succeed (default limit = 3)
    for _ in range(3):
        res = client.post(url, data=form_payload, REMOTE_ADDR=client_ip, follow=True)
        assert res.status_code == 200

    assert ContactMessage.objects.filter(ip_address=client_ip).count() == 3

    # 4th submission from same IP is throttled
    response_fourth = client.post(
        url,
        data=form_payload,
        REMOTE_ADDR=client_ip,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response_fourth.status_code == 400
    json_resp = response_fourth.json()
    assert "errors" in json_resp
    assert any("Too many messages" in str(err) for err in json_resp["errors"].values())

    # Database records count remains 3
    assert ContactMessage.objects.filter(ip_address=client_ip).count() == 3


@pytest.mark.django_db
def test_rate_limiting_is_isolated_between_different_ips(client):
    url = reverse("contact:submit")
    ip_spammer = "192.0.2.10"
    ip_clean_user = "192.0.2.20"

    form_payload = {
        "sender_name": "User",
        "email": "user@domain.com",
        "message": "Testing IP isolation mechanics.",
        "website": "",
    }

    # Exhaust limit for spammer IP
    for _ in range(3):
        client.post(url, data=form_payload, REMOTE_ADDR=ip_spammer)

    # Spammer IP is blocked
    res_blocked = client.post(
        url,
        data=form_payload,
        REMOTE_ADDR=ip_spammer,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert res_blocked.status_code == 400

    # Clean IP succeeds without interruption
    res_clean = client.post(url, data=form_payload, REMOTE_ADDR=ip_clean_user, follow=True)
    assert res_clean.status_code == 200
    assert ContactMessage.objects.filter(ip_address=ip_clean_user).count() == 1


@pytest.mark.django_db
def test_xss_payload_in_message_is_stored_cleanly_without_execution(client):
    url = reverse("contact:submit")
    xss_content = '<script>alert("xss")</script><img src=x onerror=alert(1)>'

    form_data = {
        "sender_name": "<script>Hacker</script>",
        "email": "hacker@test.com",
        "message": xss_content,
        "website": "",
    }

    response = client.post(url, data=form_data, REMOTE_ADDR="198.51.100.99", follow=True)
    assert response.status_code == 200

    # Confirm raw message stored as plain text in database
    saved = ContactMessage.objects.filter(email="hacker@test.com").first()
    assert saved is not None
    assert "<script>" in saved.message

    # Script tags must not execute unescaped in HTML response
    html = response.content.decode()
    assert '<script>alert("xss")</script>' not in html
