from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.portfolio.models import Project


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return ["portfolio:home"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return Project.objects.published().order_by("order", "-id")

    def location(self, obj):
        return reverse("portfolio:project_detail", kwargs={"slug": obj.slug})
