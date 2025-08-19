import logging
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle

from ...models import InstrumentModel
from ..serializers import InstrumentSerializer


logger = logging.getLogger("scraping_api")


class InstrumentListView(ListAPIView):
    queryset = InstrumentModel.objects.filter(enabled=True)
    serializer_class = InstrumentSerializer

    throttle_scope = "scraping"
    throttle_classes = [ScopedRateThrottle]

    @extend_schema(description="List all available instruments.")
    def get(self, request: Request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
