from django.contrib import admin
from django.utils.timezone import now
from ..models import TelegramUserModel
from django.utils.timesince import timesince


@admin.register(TelegramUserModel)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        "user_id",
        "name",
        "status",
        "usage",
        "created_at",
        "formatted_last_seen",
    ]

    ordering = ("-created_at",)
    list_filter = ("status", "is_bot", "is_premium")
    search_fields = ("username", "first_name", "last_name")

    readonly_fields = (
        "user_id",
        "username",
        "first_name",
        "last_name",
        "is_bot",
        "language_code",
        "is_premium",
        "created_at",
        "last_seen",
    )

    fieldsets = (
        (
            "Info",
            {
                "fields": (
                    "user_id",
                    "username",
                    "first_name",
                    "last_name",
                    "language_code",
                    "preferred_language",
                    "created_at",
                    "last_seen",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "requests",
                    "max_requests",
                    "is_bot",
                    "is_premium",
                )
            },
        ),
    )

    def name(self, obj):
        return f"{obj}"

    name.short_description = "Name"

    def usage(self, obj):
        return f"{obj.requests}/{obj.max_requests}"

    usage.short_description = "Usage"

    def formatted_last_seen(self, obj):
        """
        Return last_seen in human-readable relative time (e.g., '5 minutes ago').
        """
        if obj.last_seen:
            delta = timesince(obj.last_seen, now())
            return f"{delta} ago"
        return "Never"

    formatted_last_seen.short_description = "Last Seen"
