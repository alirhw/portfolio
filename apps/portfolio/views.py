from django.views.generic import TemplateView

from apps.portfolio.models import PortfolioProfile, Project, Skill


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = PortfolioProfile.objects.first()
        context["skills"] = Skill.objects.filter(highlight=True).select_related("category")
        context["projects"] = Project.objects.published().prefetch_related("technologies")[:6]
        return context
