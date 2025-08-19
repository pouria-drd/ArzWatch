import logging
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema
from django.db.models.functions import Coalesce
from rest_framework.throttling import ScopedRateThrottle
from django.db.models import Prefetch, OuterRef, Subquery
from django_filters.rest_framework import DjangoFilterBackend

from ..serializers import InstrumentSerializer
from ...models import InstrumentModel, PriceTickModel


logger = logging.getLogger("scraping_api")


@extend_schema(
    description="List all available instruments with their latest enabled price tick.",
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

        # Subquery: latest tick from default source (if exists and enabled)
        default_tick_subquery = PriceTickModel.objects.filter(
            instrument=OuterRef("pk"),
            source=OuterRef("default_source"),
            source__enabled=True,
        ).order_by("-timestamp")

        # Subquery: latest tick from any enabled source
        fallback_tick_subquery = PriceTickModel.objects.filter(
            instrument=OuterRef("pk"),
            source__enabled=True,
        ).order_by("-timestamp")

        qs = qs.annotate(
            default_tick_id=Subquery(default_tick_subquery.values("id")[:1]),
            fallback_tick_id=Subquery(fallback_tick_subquery.values("id")[:1]),
            latest_tick_id=Coalesce(
                Subquery(default_tick_subquery.values("id")[:1]),
                Subquery(fallback_tick_subquery.values("id")[:1]),
            ),
        )

        return qs.prefetch_related(
            Prefetch(
                "price_ticks",
                queryset=PriceTickModel.objects.all(),
                to_attr="all_price_ticks",
            )
        )
