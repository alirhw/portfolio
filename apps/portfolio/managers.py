from django.db import models

from .querysets import PublishedProjectQuerySet


class PublishedProjectManager(models.Manager.from_queryset(PublishedProjectQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)
