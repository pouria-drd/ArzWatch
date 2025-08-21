import logging
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Subquery

from rest_framework import exceptions
from rest_framework.generics import ListAPIView
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


from ...utils import parse_iso_dt
from ...models import InstrumentModel, PriceTickModel
from ..serializers import InstrumentSerializer, PriceTickSerializer

logger = logging.getLogger("scraping_api")


@extend_schema(
    description="List all available instruments with their latest enabled price tick "
    "(prefers default source, falls back to any enabled source).",
    parameters=[
        OpenApiParameter(
            name="category",
            location=OpenApiParameter.QUERY,
            required=False,
            type=str,
            description="Filter by category: gold | coin | currency | crypto",
        ),
        OpenApiParameter(
            name="limit",
            location=OpenApiParameter.QUERY,
            required=False,
            type=int,
            description="Pagination: number of items to return (if you add pagination later)",
        ),
        OpenApiParameter(
            name="offset",
            location=OpenApiParameter.QUERY,
            required=False,
            type=int,
            description="Pagination: number of items to skip",
        ),
    ],
    responses={200: InstrumentSerializer(many=True)},
    tags=["Instruments"],
)
class InstrumentListView(ListAPIView):
    """
    List all available instruments with their latest enabled price tick
    (prefers default source, falls back to any enabled source).

    Query params:
      - category (optional): filter by category (gold, coin, currency, crypto)
    """

    serializer_class = InstrumentSerializer

    throttle_scope = "scraping"
    throttle_classes = [ScopedRateThrottle]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category"]

    def get_queryset(self):
        qs = InstrumentModel.objects.filter(enabled=True)

        category = self.request.query_params.get("category")  # type: ignore
        if category:
            qs = qs.filter(category=category)

        # ---------- Subqueries ----------
        # Last tick from default source (if exists and enabled)
        default_latest = PriceTickModel.objects.filter(
            instrument=OuterRef("pk"),
            source=OuterRef("default_source"),
            source__enabled=True,
        ).order_by("-timestamp")

        # Last tick from any enabled source (falls back to default source)
        fallback_latest = PriceTickModel.objects.filter(
            instrument=OuterRef("pk"),
            source__enabled=True,
        ).order_by("-timestamp")

        # ---------- Annotate IDs ----------
        qs = qs.annotate(
            default_tick_id=Subquery(default_latest.values("id")[:1]),
            fallback_tick_id=Subquery(fallback_latest.values("id")[:1]),
        )

        # ---------- Annotate values for default/fallback ----------
        qs = qs.annotate(
            default_price=Subquery(default_latest.values("price")[:1]),
            default_currency=Subquery(default_latest.values("currency")[:1]),
            default_timestamp=Subquery(default_latest.values("timestamp")[:1]),
            default_meta=Subquery(default_latest.values("meta")[:1]),
            fallback_price=Subquery(fallback_latest.values("price")[:1]),
            fallback_currency=Subquery(fallback_latest.values("currency")[:1]),
            fallback_timestamp=Subquery(fallback_latest.values("timestamp")[:1]),
            fallback_meta=Subquery(fallback_latest.values("meta")[:1]),
        )

        # ---------- Final (prefer default, else fallback) ----------
        qs = qs.annotate(
            latest_tick_id=Coalesce("default_tick_id", "fallback_tick_id"),
            latest_price=Coalesce("default_price", "fallback_price"),
            latest_currency=Coalesce("default_currency", "fallback_currency"),
            latest_timestamp=Coalesce("default_timestamp", "fallback_timestamp"),
            latest_meta=Coalesce("default_meta", "fallback_meta"),
        )

        return qs


@extend_schema(
    description=(
        "Returns raw price ticks for a given instrument over a time window. "
        "Ascending by default; pass `order=desc` for newest-first."
    ),
    parameters=[
        OpenApiParameter(
            name="symbol",
            location=OpenApiParameter.QUERY,
            required=True,
            type=str,
            description="Instrument symbol (e.g., USD, EUR, BTC). Case-insensitive.",
        ),
        OpenApiParameter(
            name="from",
            location=OpenApiParameter.QUERY,
            required=False,
            type=str,
            description="Start datetime/date (ISO). Example: 2025-08-20T00:00:00Z or 2025-08-20",
        ),
        OpenApiParameter(
            name="to",
            location=OpenApiParameter.QUERY,
            required=False,
            type=str,
            description="End datetime/date (ISO).",
        ),
        OpenApiParameter(
            name="order",
            location=OpenApiParameter.QUERY,
            required=False,
            type=str,
            description="Sort by timestamp: 'asc' (default) or 'desc'.",
        ),
        OpenApiParameter(
            name="currency",
            location=OpenApiParameter.QUERY,
            required=False,
            type=str,
            description="Filter by currency code (IRR, USD, USDT, ...).",
        ),
        # default DRF pagination params (if enabled globally)
        OpenApiParameter(
            name="limit",
            location=OpenApiParameter.QUERY,
            required=False,
            type=int,
            description="Pagination: number of items to return (uses global DRF pagination).",
        ),
        OpenApiParameter(
            name="offset",
            location=OpenApiParameter.QUERY,
            required=False,
            type=int,
            description="Pagination: number of items to skip (uses global DRF pagination).",
        ),
    ],
    examples=[
        OpenApiExample(
            "BTC history (ASC)",
            summary="BTC history ascending",
            value={"symbol": "BTC", "order": "asc", "limit": 100},
        ),
        OpenApiExample(
            "USD range (DESC)",
            summary="USD within range (desc)",
            value={
                "symbol": "USD",
                "from": "2025-08-20",
                "to": "2025-08-21",
                "order": "desc",
            },
        ),
    ],
    responses={200: PriceTickSerializer(many=True)},
    tags=["Instruments"],
)
class InstrumentHistoryView(ListAPIView):
    """
    Returns raw ticks for a given instrument over a time window.

    Query params:
      - symbol (required): e.g. USD, EUR, BTC
      - from (optional, ISO): e.g. 2025-08-20T00:00:00Z or 2025-08-20
      - to   (optional, ISO)
      - order (optional): 'asc' (default) or 'desc'
      - currency (optional): filter by currency code (IRR, USD, USDT, ...)

    Pagination:
      - Uses the project's default DRF pagination (e.g., LimitOffset).

    Notes:
      - If 'from'/'to' are omitted, returns recent ticks (ordered by `order`).
      - 'from' must be <= 'to' when both provided.
    """

    serializer_class = PriceTickSerializer
    throttle_scope = "scraping"
    throttle_classes = [ScopedRateThrottle]

    def get_queryset(self):
        symbol = (self.request.query_params.get("symbol") or "").upper()  # type: ignore
        if not symbol:
            raise exceptions.ValidationError(
                {"symbol": "This query parameter is required."}
            )

        try:
            inst = InstrumentModel.objects.get(symbol__iexact=symbol, enabled=True)
        except InstrumentModel.DoesNotExist:
            raise exceptions.NotFound(
                detail=f"Instrument '{symbol}' not found or disabled."
            )

        qs = PriceTickModel.objects.filter(instrument=inst).select_related(
            "source", "instrument"
        )

        # currency filter
        cur = self.request.query_params.get("currency")  # type: ignore
        if cur:
            qs = qs.filter(currency=cur.upper())

        # time range
        dt_from = parse_iso_dt(self.request.query_params.get("from"))  # type: ignore
        dt_to = parse_iso_dt(self.request.query_params.get("to"))  # type: ignore

        if dt_from and dt_to and dt_from > dt_to:
            raise exceptions.ValidationError({"from": "must be <= to"})

        if dt_from:
            qs = qs.filter(timestamp__gte=dt_from)
        if dt_to:
            qs = qs.filter(timestamp__lte=dt_to)

        order = (self.request.query_params.get("order") or "asc").lower()  # type: ignore
        if order not in ("asc", "desc"):
            raise exceptions.ValidationError({"order": "must be 'asc' or 'desc'"})

        return qs.order_by("timestamp" if order == "asc" else "-timestamp")
