import pytest
from django.urls import reverse

from apps.contact.models import ContactMessage


@pytest.mark.django_db
def test_contact_form_view_successful_submission_creates_record(client):
    url = reverse("contact:submit")
    form_data = {
        "sender_name": "Sarah Connor",
        "email": "sarah@resistance.org",
        "message": "We need help building a resilient backend system.",
        "website": "",
    }

    response = client.post(url, data=form_data, follow=True)
    assert response.status_code == 200

    # Verify record in database
    saved_msg = ContactMessage.objects.filter(email="sarah@resistance.org").first()
    assert saved_msg is not None
    assert saved_msg.sender_name == "Sarah Connor"


@pytest.mark.django_db
def test_contact_form_view_ajax_request_returns_json(client):
    url = reverse("contact:submit")
    form_data = {
        "sender_name": "AJAX User",
        "email": "ajax@test.com",
        "message": "Testing JSON payload response from contact view.",
        "website": "",
    }

    response = client.post(
        url,
        data=form_data,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
