from django.db import models


class PublishedProjectQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def featured(self):
        return self.filter(is_featured=True)
