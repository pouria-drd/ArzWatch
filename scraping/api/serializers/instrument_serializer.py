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
        fields = ["name", "symbol", "category", "latestPriceTick"]

    def get_latestPriceTick(self, obj):
        if not getattr(obj, "latest_tick_id", None):
            return None
        return {
            "price": obj.latest_price,
            "currency": obj.latest_currency,
            "timestamp": obj.latest_timestamp,
            "meta": obj.latest_meta or {},
            "isFallback": (obj.default_tick_id is None)
            or (obj.latest_tick_id != obj.default_tick_id),
        }
