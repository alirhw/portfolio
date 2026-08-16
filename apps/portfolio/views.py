from django.http import FileResponse, Http404
from django.views import View
from django.views.generic import DetailView, TemplateView

from .models import (
    CurrentlyBuilding,
    Education,
    Experience,
    PortfolioProfile,
    Project,
    Resume,
    Skill,
    SkillCategory,
)


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["profile"] = PortfolioProfile.objects.first()
        context["has_resume"] = Resume.objects.filter(is_current=True).exists()

        context["skill_categories"] = (
            SkillCategory.objects.prefetch_related("skills")
            .filter(skills__highlight=True)
            .distinct()
        )

        context["experiences"] = Experience.objects.order_by("-start_date", "order")
        context["educations"] = Education.objects.order_by("-graduation_year", "order")

        context["currently_building"] = CurrentlyBuilding.objects.filter(is_active=True).order_by(
            "order", "-id"
        )

        context["projects"] = Project.objects.published().prefetch_related("technologies")[:6]

        context["skills"] = Skill.objects.filter(highlight=True).select_related("category")

        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "portfolio/project_detail.html"
    context_object_name = "project"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Project.objects.published().prefetch_related("technologies")


class ResumeDownloadView(View):
    def get(self, request, *args, **kwargs):
        resume = Resume.get_current()
        if not resume or not resume.file:
            raise Http404("Resume not found")

        response = FileResponse(resume.file.open("rb"), content_type="application/pdf")
        filename = resume.file.name.split("/")[-1]
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
