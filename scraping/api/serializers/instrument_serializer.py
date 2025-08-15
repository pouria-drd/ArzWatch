from rest_framework import serializers
from ...models import InstrumentModel


class InstrumentSerializer(serializers.ModelSerializer):
    updatedAt = serializers.DateTimeField(read_only=True, source="updated_at")
    createdAt = serializers.DateTimeField(read_only=True, source="created_at")

    class Meta:
        model = InstrumentModel
        fields = [
            "id",
            "name",
            "symbol",
            "category",
            "enabled",
            "updatedAt",
            "createdAt",
        ]
        read_only_fields = ["id", "name", "symbol", "category", "enabled"]
