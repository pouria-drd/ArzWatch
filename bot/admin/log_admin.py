import os
from collections import deque

from django.db import models
from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, reverse


class LogViewer(models.Model):
    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Logs"
        managed = False


@admin.register(LogViewer)
class LogAdmin(admin.ModelAdmin):
    change_list_template = "admin/log_viewer.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.admin_site.admin_view(self.view_logs), name="view-logs"),
            path("logs/", self.admin_site.admin_view(self.view_logs), name="view-logs"),
        ]
        return custom_urls + urls

    def view_logs(self, request):
        log_file_path = os.path.join(settings.BASE_DIR, "logs", "telegram_bot.log")
        lines_to_show = int(request.GET.get("lines", 50))  # Default to 50 lines

        try:
            with open(log_file_path, "r", encoding="utf-8") as log_file:
                last_lines = deque(log_file, maxlen=lines_to_show)
                log_content = "".join(last_lines)
        except FileNotFoundError:
            log_content = "Log file not found."
        except Exception as e:
            log_content = f"Error reading log file: {str(e)}"

        context = {
            "log_content": log_content,
            "lines": lines_to_show,
            "title": "Recent Logs",
        }
        return render(request, "admin/log_viewer.html", context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["logs_link"] = reverse("admin:view-logs")
        return super().changelist_view(request, extra_context=extra_context)
