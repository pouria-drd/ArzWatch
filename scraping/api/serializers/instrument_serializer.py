from rest_framework import serializers
from ...models import InstrumentModel, PriceTickModel


class InstrumentPriceTickSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceTickModel
        fields = [
            "price",
            "currency",
            "timestamp",
            "meta",
        ]


class InstrumentSerializer(serializers.ModelSerializer):
    latestPriceTick = serializers.SerializerMethodField()

    class Meta:
        model = InstrumentModel
        fields = [
            "name",
            "symbol",
            "category",
            "latestPriceTick",
        ]
        read_only_fields = [
            "name",
            "symbol",
            "category",
        ]

    def get_latestPriceTick(self, obj):
        ticks = getattr(obj, "filtered_price_ticks", [])
        if ticks:  # list is already ordered by -timestamp from queryset
            return InstrumentPriceTickSerializer(ticks[0]).data
        return None
