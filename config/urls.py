from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.portfolio.sitemaps import ProjectSitemap, StaticViewSitemap
from apps.portfolio.views import robots_txt_view

sitemaps = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
}

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("robots.txt", robots_txt_view, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("contact/", include("apps.contact.urls", namespace="contact")),
    path("", include("apps.portfolio.urls", namespace="portfolio")),
    prefix_default_language=True,
)
