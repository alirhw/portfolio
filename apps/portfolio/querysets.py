from django.db import models


class PublishedProjectQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def featured(self):
        return self.filter(is_featured=True)

    def with_technologies(self):
        return self.prefetch_related("technologies")


class SkillQuerySet(models.QuerySet):
    def with_category(self):
        return self.select_related("category")

    def highlighted(self):
        return self.filter(highlight=True)
