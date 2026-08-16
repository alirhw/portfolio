from django.urls import path

from .views import HomeView, ProjectDetailView, ResumeDownloadView

app_name = "portfolio"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("resume/", ResumeDownloadView.as_view(), name="resume_download"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="project_detail"),
]
