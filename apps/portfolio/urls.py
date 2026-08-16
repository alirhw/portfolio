from django.urls import path

from .views import HomeView, ProjectDetailView

app_name = "portfolio"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="project_detail"),
]
