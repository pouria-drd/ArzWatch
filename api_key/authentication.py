import logging
from .models import APIKey
from typing import Optional, Tuple

from django.http import HttpRequest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication


logger = logging.getLogger("api_key")


class APIKeyAuthentication(BaseAuthentication):
    """
    Custom DRF authentication using API keys.
    Usage:
        Authorization: Api-Key <key>
    """

    def authenticate(self, request: HttpRequest) -> Optional[Tuple[None, None]]:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise AuthenticationFailed("API Key required in 'Authorization' header.")

        if not auth_header.startswith("Api-Key "):
            raise AuthenticationFailed("Invalid header format. Use 'Api-Key <key>'.")

        key = auth_header[len("Api-Key ") :].strip()

        try:
            api_key_obj = APIKey.objects.get(key=key)
        except APIKey.DoesNotExist:
            logger.warning("Invalid API Key attempted: %s", key)
            raise AuthenticationFailed("Invalid API Key.")

        if not api_key_obj.is_valid():
            logger.warning("Expired or invalid API Key attempted: %s", key)
            raise AuthenticationFailed(
                "API Key expired, inactive, or exceeded usage limits."
            )

        api_key_obj.increment_usage()
        logger.info(
            "API Key used: %s (%s requests/%s max)",
            api_key_obj.name,
            api_key_obj.request_count,
            api_key_obj.max_requests,
        )

        return None, None  # No user object; authentication purely key-based
