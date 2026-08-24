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

    @property
    def position(self):
        from django.utils.translation import get_language

        lang = get_language()
        if lang and lang.startswith("fa") and self.position_fa:
            return self.position_fa
        return self.position_en

    @property
    def company_name(self):
        return self.company

    @property
    def description(self):
        from django.utils.translation import get_language

        lang = get_language()
        if lang and lang.startswith("fa") and self.description_fa:
            return self.description_fa
        return self.description_en


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

    @property
    def degree(self):
        from django.utils.translation import get_language

        lang = get_language()
        if lang and lang.startswith("fa") and self.degree_fa:
            return self.degree_fa
        return self.degree_en

    @property
    def institution(self):
        from django.utils.translation import get_language

        lang = get_language()
        if lang and lang.startswith("fa") and self.institution_fa:
            return self.institution_fa
        return self.institution_en

    @property
    def field_of_study(self):
        from django.utils.translation import get_language

        lang = get_language()
        if lang and lang.startswith("fa") and self.field_of_study_fa:
            return self.field_of_study_fa
        return self.field_of_study_en


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

    @property
    def title(self):
        from django.utils.translation import get_language

        lang = get_language()
        if lang and lang.startswith("fa") and self.title_fa:
            return self.title_fa
        return self.title_en

    @property
    def description(self):
        from django.utils.translation import get_language

        lang = get_language()
        if lang and lang.startswith("fa") and self.description_fa:
            return self.description_fa
        return self.description_en

    @property
    def current_phase(self):
        from django.utils.translation import get_language

        lang = get_language()
        if lang and lang.startswith("fa") and self.current_phase_fa:
            return self.current_phase_fa
        return self.current_phase_en
