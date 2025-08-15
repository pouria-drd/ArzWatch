from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle

from ...models import SourceModel
from ..serializers import SourceSerializer


class SourceListView(ListAPIView):
    queryset = SourceModel.objects.all()
    serializer_class = SourceSerializer

    throttle_scope = "scraping"
    throttle_classes = [ScopedRateThrottle]

    @extend_schema(description="List all available sources.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
