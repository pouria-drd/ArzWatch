import logging
from rest_framework import status
from django.core.cache import cache
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import RetrieveAPIView, ListAPIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from ..filters import PriceTickFilter
from ..serializers import PriceTickSerializer
from ...models import PriceTickModel, InstrumentModel

logger = logging.getLogger("scraping_api")


class LatestPriceView(RetrieveAPIView):
    queryset = PriceTickModel.objects.all()
    serializer_class = PriceTickSerializer

    ordering = ["-timestamp"]  # Default sorting by latest timestamp
    lookup_field = "instrument__symbol"

    throttle_scope = "scraping"
    throttle_classes = [ScopedRateThrottle]

    @extend_schema(
        description="Retrieve the latest price tick for a specific instrument symbol. "
        "Tries to use the instrument's default source first, falling back to any enabled source if unavailable.",
        parameters=[OpenApiParameter(name="symbol", type=str, location="path")],
    )
    def get(self, request: Request, *args, **kwargs):
        symbol = kwargs["instrument__symbol"].upper()
        cache_key = f"latest_price_{symbol}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for latest price of {symbol}")
            return Response(cached_data)

        try:
            instrument = InstrumentModel.objects.get(enabled=True, symbol=symbol)
        except InstrumentModel.DoesNotExist:
            logger.error(f"Instrument {symbol} not found or disabled")
            return Response(
                {"error": f"Instrument {symbol} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        price_tick = None

        # Try default source first if available and enabled
        if instrument.default_source and instrument.default_source.enabled:
            price_tick = (
                PriceTickModel.objects.filter(
                    instrument=instrument, source=instrument.default_source
                )
                .order_by("-timestamp")
                .first()
            )

        # Fallback: use any enabled source
        if not price_tick:
            price_tick = (
                PriceTickModel.objects.filter(
                    instrument=instrument, source__enabled=True
                )
                .order_by("-timestamp")
                .first()
            )

        if not price_tick:
            logger.error(f"No price data found for {symbol}")
            return Response(
                {"error": f"No price data found for {symbol}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(price_tick)
        cache.set(cache_key, serializer.data, timeout=300)  # Cache for 5 minutes
        logger.info(f"Fetched latest price for {symbol}")
        return Response(serializer.data)


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
        description="List price ticks with optional filters. "
        "Defaults to the instrument's default source, falling back to any enabled source.",
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

        # Apply default source preference with fallback
        instrument_symbol = self.request.query_params.get("instrument__symbol")
        if instrument_symbol:
            try:
                instrument = InstrumentModel.objects.get(
                    symbol=instrument_symbol, enabled=True
                )
                if instrument.default_source and instrument.default_source.enabled:
                    queryset = queryset.filter(
                        instrument=instrument, source=instrument.default_source
                    )
                else:
                    queryset = queryset.filter(
                        instrument=instrument, source__enabled=True
                    )
            except InstrumentModel.DoesNotExist:
                logger.warning(f"Instrument {instrument_symbol} not found or disabled")
                queryset = queryset.none()
        else:
            queryset = queryset.filter(source__enabled=True, instrument__enabled=True)

        return queryset
