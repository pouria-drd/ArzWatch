from django.urls import path
from .views import (
    InstrumentListView,
    SourceListView,
    LatestPriceView,
    PriceTickListView,
)

urlpatterns = [
    # List all available instruments
    path("instruments/", InstrumentListView.as_view(), name="instrument-list"),
    # List all available sources
    path("sources/", SourceListView.as_view(), name="source-list"),
    # List price ticks with filtering and pagination
    path("prices/", PriceTickListView.as_view(), name="price-list"),
    # Retrieve the latest price for a specific instrument
    path(
        "prices/latest/<str:instrument__symbol>/",
        LatestPriceView.as_view(),
        name="latest-price",
    ),
]
