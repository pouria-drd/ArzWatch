from asgiref.sync import sync_to_async
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from scraping.api.serializers import InstrumentSerializer
from scraping.models import InstrumentModel, PriceTickModel


async def fetch_instruments(category: str) -> dict:
    """
    Fetch instruments of a given category (optional) with the latest tick.
    Returns serialized data as dict, including a localized category name.
    """

    def get_queryset():
        qs = InstrumentModel.objects.filter(enabled=True)
        if category:
            qs = qs.filter(category=category)

        default_latest = PriceTickModel.objects.filter(
            instrument=OuterRef("pk"),
            source=OuterRef("default_source"),
            source__enabled=True,
        ).order_by("-timestamp")

        fallback_latest = PriceTickModel.objects.filter(
            instrument=OuterRef("pk"),
            source__enabled=True,
        ).order_by("-timestamp")

        qs = qs.annotate(
            default_tick_id=Subquery(default_latest.values("id")[:1]),
            fallback_tick_id=Subquery(fallback_latest.values("id")[:1]),
        )

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

        qs = qs.annotate(
            latest_tick_id=Coalesce("default_tick_id", "fallback_tick_id"),
            latest_price=Coalesce("default_price", "fallback_price"),
            latest_currency=Coalesce("default_currency", "fallback_currency"),
            latest_timestamp=Coalesce("default_timestamp", "fallback_timestamp"),
            latest_meta=Coalesce("default_meta", "fallback_meta"),
        )

        return qs

    queryset = await sync_to_async(list)(get_queryset())
    serializer = InstrumentSerializer(queryset, many=True)
    data = {"results": serializer.data, "count": len(serializer.data)}

    return data
