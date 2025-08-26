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
    faName = serializers.CharField(source="fa_name", read_only=True)

    class Meta:
        model = InstrumentModel
        fields = ["name", "faName", "symbol", "category", "latestPriceTick"]
        read_only_fields = [
            "id",
            "name",
            "faName",
            "symbol",
            "category",
            "latestPriceTick",
            "default_source",
            "enabled",
            "updated_at",
            "created_at",
        ]

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
