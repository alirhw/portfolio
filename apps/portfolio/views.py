from django.http import FileResponse, Http404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, TemplateView

from integrations.github.services import GitHubStatsService

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

        profile = PortfolioProfile.objects.first()
        context["profile"] = profile
        context["has_resume"] = Resume.objects.filter(is_current=True).exists()

        skill_categories = list(
            SkillCategory.objects.prefetch_related("skills")
            .filter(skills__highlight=True)
            .distinct()
        )
        context["skill_categories"] = skill_categories

        context["experiences"] = Experience.objects.order_by("-start_date", "order")
        context["educations"] = Education.objects.order_by("-graduation_year", "order")

        context["currently_building"] = CurrentlyBuilding.objects.filter(is_active=True).order_by(
            "order", "-id"
        )

        projects = list(Project.objects.published().prefetch_related("technologies")[:6])
        context["projects"] = projects

        context["skills"] = Skill.objects.filter(highlight=True).select_related("category")

        # Fetch GitHub metrics with cache and safe fallback
        github_service = GitHubStatsService()
        github_stats = github_service.get_stats()
        context["github_stats"] = github_stats

        # Prepare unified data dictionary for interactive terminal
        context["terminal_data"] = {
            "contact": {
                "name": profile.full_name if profile else "Ali Developer",
                "email": profile.email if profile else "",
                "github": profile.github_url if profile else "",
                "linkedin": profile.linkedin_url if profile else "",
            },
            "skills": [
                {
                    "category": cat.name,
                    "skills": [s.name for s in cat.skills.all() if s.highlight],
                }
                for cat in skill_categories
            ],
            "projects": [
                {
                    "title": p.title,
                    "summary": p.summary,
                    "slug": p.slug,
                    "url": reverse("portfolio:project_detail", kwargs={"slug": p.slug}),
                    "technologies": [t.name for t in p.technologies.all()],
                }
                for p in projects
            ],
            "stats": {
                "contributions": github_stats.total_contributions,
                "repos": github_stats.public_repos_count,
                "stars": github_stats.total_stars_earned,
                "streak": github_stats.current_streak_days,
            },
        }

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
