import logging
from django.db.models import Prefetch
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle
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

        return qs.prefetch_related(
            Prefetch(
                "price_ticks",
                queryset=PriceTickModel.objects.filter(source__enabled=True).order_by(
                    "-timestamp"
                ),
                to_attr="filtered_price_ticks",
            )
        )
