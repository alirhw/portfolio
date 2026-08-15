from django.db import models

from apps.portfolio.querysets import SkillQuerySet


class SkillCategory(models.Model):
    name_en = models.CharField(max_length=100)
    name_fa = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"
        ordering = ["order", "name_en"]

    def __str__(self):
        return self.name_en


class Skill(models.Model):
    class Proficiency(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        EXPERT = "expert", "Expert"

    name_en = models.CharField(max_length=100)
    name_fa = models.CharField(max_length=100)
    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.PROTECT,
        related_name="skills",
    )
    proficiency = models.CharField(
        max_length=20,
        choices=Proficiency.choices,
        default=Proficiency.INTERMEDIATE,
    )
    highlight = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    objects = models.Manager.from_queryset(SkillQuerySet)()

    class Meta:
        ordering = ["order", "name_en"]

    def __str__(self):
        return self.name_en


class Technology(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = "Technologies"
        ordering = ["name"]

    def __str__(self):
        return self.name
