from django.contrib import admin
from ..models import InstrumentModel, PriceTickModel


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


@admin.register(InstrumentModel)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = [
        "symbol",
        "name",
        "fa_name",
        "category",
        "default_source",
        # "get_price_tick_count",
        "enabled",
        "created_at",
        "updated_at",
    ]

    ordering = ["symbol"]
    list_filter = ["category"]
    list_editable = ["enabled"]
    search_fields = ["symbol", "name", "fa_name"]

    # inlines = [PriceTickInline]
    actions = ["enable_sources", "disable_sources"]

    # def get_price_tick_count(self, obj):
    #     return obj.price_ticks.all().count()

    # get_price_tick_count.short_description = "Price Ticks"

    def enable_sources(self, request, queryset):
        queryset.update(enabled=True)

    enable_sources.short_description = "Enable selected sources"

    def disable_sources(self, request, queryset):
        queryset.update(enabled=False)

    disable_sources.short_description = "Disable selected sources"
