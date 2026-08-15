from django.contrib import admin, messages

from apps.portfolio.models import (
    CurrentlyBuilding,
    Education,
    Experience,
    PortfolioProfile,
    Project,
    Resume,
    Skill,
    SkillCategory,
    Technology,
)


@admin.register(PortfolioProfile)
class PortfolioProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name_en",
        "full_name_fa",
        "headline_en",
        "available_for_hire",
        "email",
    )
    search_fields = ("full_name_en", "full_name_fa", "headline_en", "email")

    def has_add_permission(self, request):
        return not PortfolioProfile.objects.exists()


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_fa", "order")
    list_editable = ["order"]
    search_fields = ("name_en", "name_fa")
    ordering = ("order", "name_en")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "name_en",
        "name_fa",
        "category",
        "proficiency",
        "highlight",
        "order",
    )
    list_editable = ["highlight", "order"]
    list_filter = ("category", "proficiency", "highlight")
    search_fields = ("name_en", "name_fa", "category__name_en", "category__name_fa")
    ordering = ("order", "name_en")


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title_en",
        "slug",
        "is_published",
        "is_featured",
        "order",
    )
    list_editable = ["is_published", "is_featured", "order"]
    list_filter = ("is_published", "is_featured", "technologies")
    search_fields = ("title_en", "title_fa", "slug", "description_en", "description_fa")
    prepopulated_fields = {"slug": ("title_en",)}
    filter_horizontal = ("technologies",)
    ordering = ("order", "-id")
    actions = [
        "publish_selected_projects",
        "unpublish_selected_projects",
    ]

    @admin.action(description="Publish selected projects")
    def publish_selected_projects(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(
            request,
            f"{updated} project(s) published successfully.",
            messages.SUCCESS,
        )

    @admin.action(description="Unpublish selected projects")
    def unpublish_selected_projects(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(
            request,
            f"{updated} project(s) unpublished successfully.",
            messages.SUCCESS,
        )


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = (
        "position_en",
        "company",
        "start_date",
        "end_date",
        "is_current",
        "order",
    )
    list_editable = ["is_current", "order"]
    list_filter = ("is_current",)
    search_fields = ("position_en", "position_fa", "company", "description_en")
    ordering = ("-start_date", "order")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = (
        "degree_en",
        "institution_en",
        "graduation_year",
        "order",
    )
    list_editable = ["order"]
    search_fields = (
        "degree_en",
        "degree_fa",
        "institution_en",
        "institution_fa",
    )
    ordering = ("-graduation_year", "order")


@admin.register(CurrentlyBuilding)
class CurrentlyBuildingAdmin(admin.ModelAdmin):
    list_display = (
        "title_en",
        "progress_percentage",
        "current_phase_en",
        "is_active",
        "order",
    )
    list_editable = ["progress_percentage", "is_active", "order"]
    list_filter = ("is_active",)
    search_fields = ("title_en", "title_fa", "current_phase_en", "current_phase_fa")
    ordering = ("order", "-id")


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("title", "version", "is_current", "created_at")
    list_editable = ["is_current"]
    list_filter = ("is_current",)
    search_fields = ("title", "version")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-is_current", "-created_at")
