from django.urls import path
from .views import InstrumentListView, SourceListView

urlpatterns = [
    # List all available instruments
    path("instruments/", InstrumentListView.as_view(), name="instrument-list"),
    # List all available sources
    path("sources/", SourceListView.as_view(), name="source-list"),
]
