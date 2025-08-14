from django.contrib import admin
from ..models import PriceTickModel


@admin.register(PriceTickModel)
class PriceTickAdmin(admin.ModelAdmin):
    list_display = [
        "source__name",
        "instrument__symbol",
        "price",
        "currency",
        "timestamp",
    ]

    list_filter = ["instrument__category", "source__enabled", "currency", "timestamp"]
    search_fields = ["instrument__symbol", "source__name", "currency", "price"]

    ordering = ["-timestamp"]
    list_per_page = 50
    date_hierarchy = "timestamp"

    raw_id_fields = [
        "instrument",
        "source",
    ]  # Use popup selectors for foreign keys to handle large datasets

    fieldsets = [
        (None, {"fields": ["instrument", "source", "currency", "timestamp"]}),
        ("Price Data", {"fields": ["price", "meta"]}),
    ]

    readonly_fields = ["timestamp"]  # Prevent editing timestamps

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("instrument", "source")
