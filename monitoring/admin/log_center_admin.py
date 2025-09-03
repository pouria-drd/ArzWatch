import os
from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse

from ..models import LogCenterModel
from ..utils import list_apps, list_log_files, tail_lines, parse_json_lines


@admin.register(LogCenterModel)
class LogCenterAdmin(admin.ModelAdmin):
    change_list_template = "log_center.html"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "download/",
                self.admin_site.admin_view(self.download),
                name="monitoring-log-download",
            ),
        ]
        return custom + urls

    def changelist_view(self, request, extra_context=None):
        apps = list_apps(settings)  # [(app, dir), ...]
        selected_app = request.GET.get("app") or (apps[0][0] if apps else None)
        n = int(request.GET.get("n", 500))
        selected_level = request.GET.get("level", "")
        selected_file = request.GET.get("file", "")

        app_dir = dict(apps).get(selected_app)
        files = list_log_files(app_dir) if selected_app else []

        if not selected_file and files:
            selected_file = files[0]

        rows = []
        if selected_app and selected_file:
            path = os.path.join(app_dir, selected_file)  # type: ignore
            lines = tail_lines(path, n=n)
            rows = parse_json_lines(lines)
            if selected_level:
                rows = [r for r in rows if r.get("level") == selected_level]

        context = {
            "title": "Log Center",
            "apps": apps,
            "selected_app": selected_app,
            "files": files,
            "selected_file": selected_file,
            "rows": rows,
            "n": n,
            "levels": ["", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        }
        if extra_context:
            context.update(extra_context)
        return TemplateResponse(request, self.change_list_template, context)

    def download(self, request):
        app = request.GET.get("app")
        file = request.GET.get("file")
        apps = dict(list_apps(settings))
        if not app or app not in apps or not file:
            raise Http404("Not found")
        path = os.path.join(apps[app], file)
        if not os.path.isfile(path):
            raise Http404("Not found")
        with open(path, "rb") as f:
            data = f.read()
        resp = HttpResponse(data, content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{file}"'
        return resp
