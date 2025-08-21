from django.urls import path
from .views import InstrumentListView, InstrumentHistoryView, SourceListView

urlpatterns = [
    # List all available sources
    path("sources/", SourceListView.as_view(), name="source-list"),
    # List all available instruments
    path("instruments/", InstrumentListView.as_view(), name="instrument-list"),
    # List all available instruments' historical quotes
    path(
        "instruments/history/",
        InstrumentHistoryView.as_view(),
        name="instrument-history",
    ),
]
