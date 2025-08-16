from rest_framework import serializers
from ...models import SourceModel, SourceConfigModel


class SourceSerializer(serializers.ModelSerializer):
    baseUrl = serializers.URLField(read_only=True, source="base_url")
    # updatedAt = serializers.DateTimeField(read_only=True, source="updated_at")
    # createdAt = serializers.DateTimeField(read_only=True, source="created_at")

    class Meta:
        model = SourceModel
        fields = [
            # "id",
            "name",
            "baseUrl",
            # "updatedAt",
            # "createdAt",
        ]
        read_only_fields = ["id", "name"]


class SourceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceConfigModel
        fields = [
            # "id",
            "source",
            "instrument",
            "path",
        ]
        read_only_fields = [
            # "id",
            "source",
            "instrument",
            "path",
        ]
