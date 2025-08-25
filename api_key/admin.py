import csv
from .models import APIKey
from datetime import timedelta
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.utils.timezone import now as django_now


class ExpiredFilter(SimpleListFilter):
    title = "Expiration Status"
    parameter_name = "expired"

    def lookups(self, request, model_admin):
        return (
            ("expired", "Expired"),
            ("active", "Active"),
            ("expiring_soon", "Expiring soon (7 days)"),
        )

    def queryset(self, request, queryset):
        now_ = django_now()
        if self.value() == "expired":
            return queryset.filter(expires_at__lt=now_)
        if self.value() == "active":
            return queryset.filter(expires_at__gte=now_) | queryset.filter(
                expires_at__isnull=True
            )
        if self.value() == "expiring_soon":
            return queryset.filter(
                expires_at__gte=now_, expires_at__lte=now_ + timedelta(days=7)
            )
        return queryset


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "masked_key",
        "request_count",
        "max_requests",
        "usage_percentage",
        "enabled",
        "created_at",
        "expires_at",
        "last_request_at",
        "expiration_status",
    )

    list_filter = ("enabled", "created_at", ExpiredFilter)
    search_fields = ("name", "key")
    readonly_fields = ("key", "created_at", "updated_at")
    date_hierarchy = "created_at"
    actions = [
        "reset_request_count",
        "activate_keys",
        "deactivate_keys",
        "extend_expiration",
        "export_as_csv",
    ]

    fieldsets = (
        ("Basic Info", {"fields": ("name", "key", "enabled")}),
        (
            "Usage Limits",
            {
                "fields": ("request_count", "max_requests", "expires_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def masked_key(self, obj: APIKey) -> str:
        return f"{obj.key[:4]}...{obj.key[-4:]}" if len(obj.key) > 8 else obj.key

    masked_key.short_description = "API Key"

    def usage_percentage(self, obj: APIKey) -> str:
        return f"{min(100, int((obj.request_count / obj.max_requests) * 100))}%"

    usage_percentage.short_description = "Usage"

    def expiration_status(self, obj: APIKey) -> str:
        if not obj.enabled:
            return format_html('<span style="color:gray;">Inactive</span>')
        if obj.expires_at:
            if obj.expires_at < django_now():
                return format_html('<span style="color:red;">Expired</span>')
            if (obj.expires_at - django_now()).days < 7:
                return format_html('<span style="color:orange;">Expires soon</span>')
        return format_html('<span style="color:green;">Active</span>')

    expiration_status.short_description = "Status"

    # --- Admin Actions ---
    def reset_request_count(self, request, queryset):
        updated = queryset.update(request_count=0)
        self.message_user(
            request, f"Reset count for {updated} key{'s' if updated != 1 else ''}."
        )

    reset_request_count.short_description = "Reset request count"

    def activate_keys(self, request, queryset):
        updated = queryset.update(enabled=True)
        self.message_user(
            request, f"Activated {updated} key{'s' if updated != 1 else ''}."
        )

    activate_keys.short_description = "Activate selected keys"

    def deactivate_keys(self, request, queryset):
        updated = queryset.update(enabled=False)
        self.message_user(
            request, f"Deactivated {updated} key{'s' if updated != 1 else ''}."
        )

    deactivate_keys.short_description = "Deactivate selected keys"

    def extend_expiration(self, request, queryset):
        for obj in queryset:
            if obj.expires_at:
                obj.expires_at += timedelta(days=30)
                obj.save(update_fields=["expires_at"])
        self.message_user(request, "Extended expiration by 30 days.")

    extend_expiration.short_description = "Extend expiration by 30 days"

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="api_keys.csv"'

        writer = csv.writer(response)
        writer.writerow(["Name", "Key", "Requests", "Max Requests", "Status"])
        for obj in queryset:
            writer.writerow(
                [
                    obj.name,
                    obj.key,
                    obj.request_count,
                    obj.max_requests,
                    "Active" if obj.enabled else "Inactive",
                ]
            )
        return response

    export_as_csv.short_description = "Export selected keys as CSV"
