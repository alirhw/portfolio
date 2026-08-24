from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.views import healthcheck_view, sentry_debug_trigger_view
from apps.portfolio.sitemaps import ProjectSitemap, StaticViewSitemap
from apps.portfolio.views import robots_txt_view

sitemaps = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
}

# Root non-i18n system endpoints
urlpatterns = [
    path("healthz/", healthcheck_view, name="healthcheck"),
    path("robots.txt", robots_txt_view, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("i18n/", include("django.conf.urls.i18n")),
    path("_debug/sentry-trigger/", sentry_debug_trigger_view, name="sentry_debug_trigger"),
]

# Multilingual user-facing routes
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("contact/", include("apps.contact.urls", namespace="contact")),
    path("", include("apps.portfolio.urls", namespace="portfolio")),
    prefix_default_language=True,
)
