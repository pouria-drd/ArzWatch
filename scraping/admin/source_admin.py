from django.contrib import admin
from django.utils.html import format_html
from ..models import SourceConfigModel, SourceModel, PriceTickModel


class PriceTickInline(admin.TabularInline):
    model = PriceTickModel
    extra = 1  # Number of empty forms to display
    fields = ["source", "price", "currency", "timestamp", "meta"]
    readonly_fields = ["timestamp"]
    ordering = ["-timestamp"]
    show_change_link = (
        True  # Allow linking to the full change form for the inline object
    )

    def has_add_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class SourceConfigInline(admin.TabularInline):
    model = SourceConfigModel
    extra = 1  # Number of empty forms to display
    fields = ["source", "instrument", "path"]
    ordering = ["source__name", "instrument__symbol"]
    show_change_link = True


@admin.register(SourceConfigModel)
class SourceConfigAdmin(admin.ModelAdmin):
    list_display = ["source", "instrument", "path"]
    list_filter = ["source", "instrument"]
    search_fields = ["source__name", "instrument__symbol"]
    ordering = ["source__name", "instrument__symbol"]


@admin.register(SourceModel)
class SourceAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "base_url_link",
        # "get_price_tick_count",
        "enabled",
        "created_at",
        "updated_at",
    ]

    ordering = ["name"]
    search_fields = ["name"]
    list_filter = ["enabled"]
    list_editable = ["enabled"]  # Allow inline editing of enabled status

    # inlines = [PriceTickInline, SourceConfigInline]
    actions = ["enable_sources", "disable_sources"]

    def base_url_link(self, obj):
        return format_html('<a href="{0}" target="_blank">{0}</a>', obj.base_url)

    base_url_link.short_description = "Base URL"

    # def get_price_tick_count(self, obj):
    #     return obj.price_ticks.all().count()

    # get_price_tick_count.short_description = "Price Ticks"

    def enable_sources(self, request, queryset):
        queryset.update(enabled=True)

    enable_sources.short_description = "Enable selected sources"

    def disable_sources(self, request, queryset):
        queryset.update(enabled=False)

    disable_sources.short_description = "Disable selected sources"
