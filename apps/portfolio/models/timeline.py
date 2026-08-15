from django.db import models


class Experience(models.Model):
    position_en = models.CharField(max_length=150)
    position_fa = models.CharField(max_length=150)

    company = models.CharField(max_length=150)
    company_url = models.URLField(blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

    description_en = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-start_date", "order"]

    def __str__(self):
        return f"{self.position_en} at {self.company}"


class Education(models.Model):
    degree_en = models.CharField(max_length=150)
    degree_fa = models.CharField(max_length=150)

    institution_en = models.CharField(max_length=200)
    institution_fa = models.CharField(max_length=200)

    field_of_study_en = models.CharField(max_length=150, blank=True)
    field_of_study_fa = models.CharField(max_length=150, blank=True)

    start_year = models.PositiveSmallIntegerField(null=True, blank=True)
    graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)

    description_en = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Education"
        ordering = ["-graduation_year", "order"]

    def __str__(self):
        return f"{self.degree_en} - {self.institution_en}"


class CurrentlyBuilding(models.Model):
    title_en = models.CharField(max_length=200)
    title_fa = models.CharField(max_length=200)

    description_en = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)

    progress_percentage = models.PositiveSmallIntegerField(
        default=0,
        help_text="Progress from 0 to 100",
    )
    current_phase_en = models.CharField(max_length=100, blank=True)
    current_phase_fa = models.CharField(max_length=100, blank=True)

    related_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Currently Building"
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title_en
