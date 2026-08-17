import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from apps.contact.models import ContactMessage

logger = logging.getLogger(__name__)


class ContactSubmissionService:
    """
    Service managing contact message persistence and notification (Persist-then-notify).
    Guarantees that email delivery failures do not compromise database persistence.
    """

    @classmethod
    def submit_message(
        cls,
        sender_name: str,
        email: str,
        message: str,
        ip_address: str | None = None,
        subject: str = "",
    ) -> ContactMessage:
        # 1. Persist Phase: Commit message to database inside atomic transaction
        with transaction.atomic():
            contact_message = ContactMessage.objects.create(
                sender_name=sender_name,
                email=email,
                message=message,
                subject=subject,
                ip_address=ip_address,
                is_notified=False,
            )

        # 2. Notify Phase: Attempt email dispatch outside the database transaction
        cls._send_notification(contact_message)

        return contact_message

    @classmethod
    def _send_notification(cls, contact_message: ContactMessage) -> None:
        recipient_email = getattr(settings, "CONTACT_NOTIFICATION_EMAIL", None)
        if not recipient_email:
            admins = getattr(settings, "ADMINS", [])
            if admins and len(admins) > 0 and len(admins[0]) > 1:
                recipient_email = admins[0][1]
            else:
                recipient_email = "admin@example.com"

        email_subject = f"[Portfolio Contact] New message from {contact_message.sender_name}"
        email_body = (
            f"Sender Name: {contact_message.sender_name}\n"
            f"Sender Email: {contact_message.email}\n"
            f"IP Address:   {contact_message.ip_address or 'Unknown'}\n"
            f"Date:         {contact_message.created_at:%Y-%m-%d %H:%M:%S}\n\n"
            f"Message Body:\n"
            f"----------------------------------------\n"
            f"{contact_message.message}\n"
            f"----------------------------------------\n"
        )

        try:
            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@portfolio.local"),
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            # Mark notification sent upon successful email delivery
            contact_message.is_notified = True
            contact_message.save(update_fields=["is_notified"])

        except Exception as exc:
            # Log SMTP/network failures without raising; database record is already safe
            logger.error(
                "Failed to send email notification for ContactMessage ID=%s: %s",
                contact_message.id,
                exc,
                exc_info=True,
            )
