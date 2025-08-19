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
        ticks = getattr(obj, "all_price_ticks", [])
        if not ticks:
            return None

        tick = next((t for t in ticks if t.id == obj.latest_tick_id), None)
        if not tick:
            return None

        data = InstrumentPriceTickSerializer(tick).data
        data["isFallback"] = tick.id != obj.default_tick_id  # type: ignore
        return data
