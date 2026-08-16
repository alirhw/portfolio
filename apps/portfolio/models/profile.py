from django.db import models


class PortfolioProfile(models.Model):
    full_name_en = models.CharField(max_length=150)
    full_name_fa = models.CharField(max_length=150)

    headline_en = models.CharField(max_length=200)
    headline_fa = models.CharField(max_length=200)

    bio_en = models.TextField()
    bio_fa = models.TextField()

    available_for_hire = models.BooleanField(default=True)

    github_url = models.URLField()
    linkedin_url = models.URLField()
    email = models.EmailField()

    singleton_key = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(singleton_key=1),
                name="portfolio_profile_singleton_key_is_one",
            ),
        ]

    def __str__(self):
        return self.full_name_en

    @property
    def full_name(self):
        return self.full_name_en

    @property
    def headline(self):
        return self.headline_en

    @property
    def bio(self):
        return self.bio_en

    @property
    def is_available(self):
        return self.available_for_hire
