from ...models import PriceTickModel
from django_filters import FilterSet, CharFilter, NumberFilter, DateTimeFilter


class PriceTickFilter(FilterSet):
    instrument__symbol = CharFilter(
        field_name="instrument__symbol", lookup_expr="exact"
    )
    instrument__symbol_contains = CharFilter(
        field_name="instrument__symbol", lookup_expr="contains"
    )
    instrument__category = CharFilter(
        field_name="instrument__category", lookup_expr="contains"
    )
    source__name = CharFilter(field_name="source__name", lookup_expr="exact")
    source__name_contains = CharFilter(
        field_name="source__name", lookup_expr="contains"
    )
    currency = CharFilter(field_name="currency", lookup_expr="exact")
    price_gte = NumberFilter(field_name="price", lookup_expr="gte")
    price_lte = NumberFilter(field_name="price", lookup_expr="lte")
    timestamp_gte = DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    timestamp_lte = DateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = PriceTickModel
        fields = [
            "instrument__symbol",
            "instrument__symbol_contains",
            "instrument__category",
            "source__name",
            "source__name_contains",
            "currency",
            "price_gte",
            "price_lte",
            "timestamp_gte",
            "timestamp_lte",
        ]

    def filter_queryset(self, queryset):
        # Convert instrument__symbol to uppercase for exact match
        symbol = self.data.get("instrument__symbol")
        if symbol:
            queryset = queryset.filter(instrument__symbol=symbol.upper())
        return super().filter_queryset(queryset)
