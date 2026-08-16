from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    sender_name = models.CharField(
        max_length=120,
        verbose_name=_("Sender Name"),
    )
    email = models.EmailField(
        max_length=254,
        verbose_name=_("Email"),
    )
    subject = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name=_("Subject"),
    )
    message = models.TextField(
        max_length=3000,
        verbose_name=_("Message"),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP Address"),
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Is Read"),
    )
    is_notified = models.BooleanField(
        default=False,
        verbose_name=_("Is Notification Sent"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["-created_at"],
                name="contact_msg_created_idx",
            ),
        ]

    def __init__(self, *args, **kwargs):
        if "name" in kwargs and "sender_name" not in kwargs:
            kwargs["sender_name"] = kwargs.pop("name")
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        if self.created_at:
            timestamp = f"{self.created_at:%Y-%m-%d %H:%M}"
            return f"Message from {self.sender_name} ({self.email}) at {timestamp}"
        return f"Message from {self.sender_name} ({self.email})"

    @property
    def name(self):
        return self.sender_name

    @name.setter
    def name(self, value):
        self.sender_name = value
