import logging
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Subquery
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend

from ..serializers import InstrumentSerializer
from ...models import InstrumentModel, PriceTickModel

logger = logging.getLogger("scraping_api")


@extend_schema(
    description="List all available instruments with their latest enabled price tick "
    "(prefers default source, falls back to any enabled source).",
    tags=["Instruments"],
)
class InstrumentListView(ListAPIView):
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
