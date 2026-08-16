from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("sender_name", "email", "created_at", "is_read", "is_notified")
    list_editable = ["is_read"]
    list_filter = ("is_read", "is_notified", "created_at")
    search_fields = ("sender_name", "email", "message")
    readonly_fields = (
        "sender_name",
        "email",
        "subject",
        "message",
        "ip_address",
        "created_at",
    )
    ordering = ("-created_at",)
    actions = ["mark_as_read"]

    @admin.action(description="Mark selected messages as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    def has_add_permission(self, request):
        return False
