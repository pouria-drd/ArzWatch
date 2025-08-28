from django.contrib import admin
from django.utils.timezone import now
from django.utils.timesince import timesince
from ..models import TelegramUserModel


@admin.register(TelegramUserModel)
class TelegramUserAdmin(admin.ModelAdmin):
    # Columns in the list view
    list_display = [
        "user_id",
        "display_name",
        "chat_id",
        "status",
        "usage_display",
        "created_at",
        "last_seen_display",
    ]

    ordering = ("-created_at",)
    list_filter = ("status", "is_bot", "is_premium")
    search_fields = ("username", "first_name", "last_name")

    # Actions
    actions = [
        "reset_requests",
        "set_active",
        "set_inactive",
        "set_banned",
    ]

    # Read-only fields
    readonly_fields = ("last_seen",)

    # Fieldsets for better organization
    fieldsets = (
        (
            "User Information",
            {
                "fields": (
                    "user_id",
                    "chat_id",
                    "username",
                    "first_name",
                    "last_name",
                    "language_code",
                    "preferred_language",
                )
            },
        ),
        (
            "Activity",
            {
                "fields": (
                    "created_at",
                    "last_seen",
                    "requests",
                    "max_requests",
                )
            },
        ),
        (
            "Status & Flags",
            {
                "fields": (
                    "status",
                    "is_bot",
                    "is_premium",
                )
            },
        ),
    )

    # ------------------- Custom Columns -------------------
    def display_name(self, obj):
        """Show the user's display name"""
        return str(obj)

    display_name.short_description = "Name"

    def usage_display(self, obj):
        """Show usage as requests/max_requests"""
        return f"{obj.requests}/{obj.max_requests}"

    usage_display.short_description = "Usage"

    def last_seen_display(self, obj):
        """Show last seen in human-readable format"""
        if obj.last_seen:
            delta = timesince(obj.last_seen, now())
            return f"{delta} ago"
        return "Never"

    last_seen_display.short_description = "Last Seen"

    # ------------------- Actions -------------------
    def reset_requests(self, request, queryset):
        queryset.update(requests=0)

    reset_requests.short_description = "Reset requests"

    def set_active(self, request, queryset):
        queryset.update(status=TelegramUserModel.Status.ACTIVE)

    set_active.short_description = "Set status to Active"

    def set_inactive(self, request, queryset):
        queryset.update(status=TelegramUserModel.Status.INACTIVE)

    set_inactive.short_description = "Set status to Inactive"

    def set_banned(self, request, queryset):
        queryset.update(status=TelegramUserModel.Status.BANNED)

    set_banned.short_description = "Set status to Banned"
