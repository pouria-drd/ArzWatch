from django.contrib import admin
from ..models import TelegramCommandModel


@admin.register(TelegramCommandModel)
class TelegramCommandAdmin(admin.ModelAdmin):
    list_display = [
        "telegram_user",
        "command_type",
        "message",
        "created_at",
    ]

    ordering = ("-created_at",)
    list_filter = ("command_type", "telegram_user")
    search_fields = ("telegram_user__username", "telegram_user__first_name", "message")
