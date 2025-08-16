from rest_framework import serializers
from ...models import PriceTickModel
from .source_serializer import SourceSerializer
from .instrument_serializer import InstrumentSerializer


class PriceTickSerializer(serializers.ModelSerializer):
    instrument = InstrumentSerializer(read_only=True)
    source = SourceSerializer(read_only=True)

    class Meta:
        model = PriceTickModel
        fields = [
            # "id",
            "instrument",
            "source",
            "price",
            "currency",
            "timestamp",
            "meta",
        ]
        read_only_fields = [
            # "id",
            "instrument",
            "source",
            "price",
            "currency",
            "timestamp",
            "meta",
        ]
