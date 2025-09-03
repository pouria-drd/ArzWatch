from django.urls import path
from .views import test, system_info_api

urlpatterns = [
    path("", test, name="test"),
    path("api/system-info/", system_info_api, name="system_info_api"),
]
