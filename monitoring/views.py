import logging
from django.http import HttpRequest
from django.http import JsonResponse

from .utils import get_system_info

logger = logging.getLogger("monitoring")


def system_info_api(request: HttpRequest):
    """Standalone API endpoint for system information"""
    response = JsonResponse(get_system_info())
    logger.info("API request received for system info")
    return response
