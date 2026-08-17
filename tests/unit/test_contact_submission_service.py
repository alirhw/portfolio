from unittest.mock import patch

import pytest
from django.core import mail

from apps.contact.models import ContactMessage
from apps.contact.services.submission import ContactSubmissionService


@pytest.mark.django_db
def test_submit_message_persists_and_sends_email_successfully():
    message_obj = ContactSubmissionService.submit_message(
        sender_name="Alice Smith",
        email="alice@example.com",
        message="I would like to hire you for a Django project.",
        ip_address="192.0.2.55",
    )

    # Check persistence in database
    assert message_obj.id is not None
    assert message_obj.sender_name == "Alice Smith"
    assert message_obj.is_notified is True

    # Check email dispatch
    assert len(mail.outbox) == 1
    sent_mail = mail.outbox[0]
    assert "Alice Smith" in sent_mail.subject
    assert "Alice Smith" in sent_mail.body
    assert "192.0.2.55" in sent_mail.body


@pytest.mark.django_db
def test_submit_message_persists_even_when_email_sending_fails():
    with patch(
        "apps.contact.services.submission.send_mail",
        side_effect=OSError("SMTP server disconnected"),
    ):
        message_obj = ContactSubmissionService.submit_message(
            sender_name="Bob Jones",
            email="bob@example.com",
            message="Testing resilience against SMTP failure.",
            ip_address="198.51.100.12",
        )

    # Message must persist successfully in database without crashing
    assert message_obj.id is not None
    assert ContactMessage.objects.filter(id=message_obj.id).exists()

    # is_notified remains False upon failure
    message_obj.refresh_from_db()
    assert message_obj.is_notified is False
