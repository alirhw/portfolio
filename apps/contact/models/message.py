from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["-created_at"],
                name="contact_msg_created_idx",
            ),
        ]

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
