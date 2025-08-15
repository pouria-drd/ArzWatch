import logging
from rest_framework import status
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import RetrieveAPIView, ListAPIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from ...models import PriceTickModel
from ..filters import PriceTickFilter
from ..serializers import PriceTickSerializer

logger = logging.getLogger("scraping_api")


class LatestPriceView(RetrieveAPIView):
    queryset = PriceTickModel.objects.all()
    serializer_class = PriceTickSerializer

    ordering = ["-timestamp"]  # Default sorting by latest timestamp
    lookup_field = "instrument__symbol"

    throttle_scope = "scraping"
    throttle_classes = [ScopedRateThrottle]

    @extend_schema(
        description="Retrieve the latest price tick for a specific instrument symbol.",
        parameters=[OpenApiParameter(name="symbol", type=str, location="path")],
    )
    def get(self, request, *args, **kwargs):
        symbol = kwargs["instrument__symbol"].upper()
        cache_key = f"latest_price_{symbol}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for latest price of {symbol}")
            return Response(cached_data)

        try:
            price_tick = PriceTickModel.objects.filter(
                instrument__symbol=symbol
            ).latest("timestamp")
            serializer = self.get_serializer(price_tick)
            cache.set(cache_key, serializer.data, timeout=300)  # Cache for 5 minutes
            logger.info(f"Fetched latest price for {symbol}")
            return Response(serializer.data)
        except PriceTickModel.DoesNotExist:
            logger.error(f"No price data found for {symbol}")
            return Response(
                {"error": f"No price data found for {symbol}"},
                status=status.HTTP_404_NOT_FOUND,
            )


class PriceTickListView(ListAPIView):
    queryset = PriceTickModel.objects.all().select_related("instrument", "source")
    serializer_class = PriceTickSerializer

    throttle_scope = "scraping"
    throttle_classes = [ScopedRateThrottle]

    filterset_class = PriceTickFilter
    filter_backends = [DjangoFilterBackend]

    ordering_fields = ["-timestamp", "price"]
    search_fields = ["instrument__symbol", "source__name"]

    ordering = ["-timestamp"]  # Default sorting by latest timestamp

    @extend_schema(
        description="List price ticks with optional filters for instrument, source, currency, price, timestamp, and source URL. Results are sorted by latest timestamp by default.",
        parameters=[
            OpenApiParameter(
                name="instrument__symbol",
                type=str,
                location="query",
                description="Exact instrument symbol (e.g., USD)",
            ),
            OpenApiParameter(
                name="instrument__symbol_contains",
                type=str,
                location="query",
                description="Partial match for instrument symbol",
            ),
            OpenApiParameter(
                name="source__name",
                type=str,
                location="query",
                description="Exact source name (e.g., tgju)",
            ),
            OpenApiParameter(
                name="source__name_contains",
                type=str,
                location="query",
                description="Partial match for source name",
            ),
            OpenApiParameter(
                name="currency",
                type=str,
                location="query",
                description="Currency code (e.g., USD, EUR, IRR)",
            ),
            OpenApiParameter(
                name="price_gte",
                type=float,
                location="query",
                description="Minimum price",
            ),
            OpenApiParameter(
                name="price_lte",
                type=float,
                location="query",
                description="Maximum price",
            ),
            OpenApiParameter(
                name="timestamp_gte",
                type=str,
                location="query",
                description="Start timestamp (YYYY-MM-DD or ISO 8601)",
            ),
            OpenApiParameter(
                name="timestamp_lte",
                type=str,
                location="query",
                description="End timestamp (YYYY-MM-DD or ISO 8601)",
            ),
            OpenApiParameter(
                name="meta__source_url",
                type=str,
                location="query",
                description="Partial match for meta.source_url (PostgreSQL only)",
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location="query",
                description="Order by 'timestamp' or 'price' (e.g., '-timestamp' for descending)",
            ),
        ],
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        # Additional validation for timestamp format
        timestamp_gte = self.request.query_params.get("timestamp_gte")
        timestamp_lte = self.request.query_params.get("timestamp_lte")
        try:
            if timestamp_gte:
                queryset = queryset.filter(timestamp__gte=timestamp_gte)
            if timestamp_lte:
                queryset = queryset.filter(timestamp__lte=timestamp_lte)
        except ValueError as e:
            logger.error(f"Invalid timestamp format: {e}")
            raise ValidationError("Timestamps must be in YYYY-MM-DD or ISO 8601 format")
        return queryset
