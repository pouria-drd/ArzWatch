from typing import Optional
from datetime import datetime

from django.utils import timezone
from django.utils.dateparse import parse_datetime


def parse_iso_dt(value: Optional[str]) -> Optional[datetime]:
    """
    Parse an ISO datetime or plain date (YYYY-MM-DD) and return a timezone-aware datetime.
    Returns None if value is falsy or cannot be parsed.

    Examples:
        parse_iso_dt("2025-08-21T10:30:00Z")
        parse_iso_dt("2025-08-21")
    """
    if not value:
        return None

    dt = parse_datetime(value)
    if not dt:
        try:
            dt = datetime.fromisoformat(value)
        except Exception:
            dt = None

    if dt and timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())

    return dt
