from django.views.generic import TemplateView

from .models import (
    Education,
    Experience,
    PortfolioProfile,
    Project,
    Skill,
    SkillCategory,
)


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["profile"] = PortfolioProfile.objects.first()

        # واکشی دسته‌بندی‌ها به همراه مهارت‌های هایلایت‌شده برای جلوگیری از N+1
        context["skill_categories"] = (
            SkillCategory.objects.prefetch_related("skills")
            .filter(skills__highlight=True)
            .distinct()
        )

        # سوابق شغلی به ترتیب نزولی (جدیدترین اول)
        context["experiences"] = Experience.objects.order_by("-start_date", "order")

        # سوابق تحصیلی به ترتیب نزولی (جدیدترین اول)
        context["educations"] = Education.objects.order_by("-graduation_year", "order")

        # ۶ پروژه منتشرشده با فناوری‌های مرتبط
        context["projects"] = Project.objects.published().prefetch_related("technologies")[:6]

        # حفظ سازگاری با کانتکست تست‌های قبلی
        context["skills"] = Skill.objects.filter(highlight=True).select_related("category")

        return context
