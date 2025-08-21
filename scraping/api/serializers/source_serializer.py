from rest_framework import serializers
from ...models import SourceModel, SourceConfigModel


class SourceSerializer(serializers.ModelSerializer):
    baseUrl = serializers.URLField(read_only=True, source="base_url")

    class Meta:
        model = SourceModel
        fields = [
            "name",
            "baseUrl",
        ]
        read_only_fields = ["id", "name"]


class SourceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceConfigModel
        fields = [
            "source",
            "instrument",
            "path",
        ]
        read_only_fields = [
            "source",
            "instrument",
            "path",
        ]
