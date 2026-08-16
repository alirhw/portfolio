from django.db import models

from apps.portfolio.managers import PublishedProjectManager
from apps.portfolio.querysets import PublishedProjectQuerySet


class Project(models.Model):
    title_en = models.CharField(max_length=200)
    title_fa = models.CharField(max_length=200)

    slug = models.SlugField(max_length=200, unique=True)

    description_en = models.TextField()
    description_fa = models.TextField()

    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    demo_url = models.URLField(blank=True)
    repository_url = models.URLField(blank=True)

    technologies = models.ManyToManyField(
        "portfolio.Technology",
        related_name="projects",
        blank=True,
    )

    order = models.PositiveIntegerField(default=0)

    objects = models.Manager.from_queryset(PublishedProjectQuerySet)()
    published_objects = PublishedProjectManager()

    class Meta:
        ordering = ["order", "-id"]
        indexes = [
            models.Index(
                fields=["is_published", "order"],
                name="project_pub_order_idx",
            ),
        ]

    def __str__(self):
        return self.title_en

    @property
    def title(self):
        return self.title_en

    @property
    def summary(self):
        return self.description_en

    @property
    def github_url(self):
        return self.repository_url

    @property
    def live_url(self):
        return self.demo_url
