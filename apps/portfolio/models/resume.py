from django.db import models


class Resume(models.Model):
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to="resumes/")
    version = models.CharField(max_length=50, blank=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Resumes"
        ordering = ["-is_current", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_current"],
                condition=models.Q(is_current=True),
                name="unique_current_resume",
            ),
        ]

    def __str__(self):
        return f"{self.title} (Current)" if self.is_current else self.title

    @classmethod
    def get_current(cls):
        return cls.objects.filter(is_current=True).order_by("-updated_at").first()
