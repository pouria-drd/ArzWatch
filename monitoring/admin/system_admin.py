from django.urls import path
from django.contrib import admin
from django.http import JsonResponse
from django.template.response import TemplateResponse

from ..utils import get_system_info
from ..models import SystemInfoModel


@admin.register(SystemInfoModel)
class SystemInfoAdmin(admin.ModelAdmin):
    change_list_template = "system_info.html"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "api/system-info/",
                self.admin_site.admin_view(self.system_info_api),
                name="system_info_api",
            ),
        ]
        return custom_urls + urls

    def system_info_api(self, request):
        """API endpoint for real-time system info updates"""
        system_info = get_system_info()
        return JsonResponse(system_info)

    def changelist_view(self, request, extra_context=None):
        context = {
            "system_info": get_system_info(),
            "title": "System Monitor Dashboard",
        }
        if extra_context:
            context.update(extra_context)
        return TemplateResponse(request, self.change_list_template, context)
