from zoneinfo import ZoneInfo
from typing import Union, Tuple, Dict
from datetime import datetime, timedelta
from persiantools.jdatetime import JalaliDateTime


def persian_date_time(dt: Union[str, datetime]) -> Tuple[str, str]:
    """
    Converts a given datetime (or ISO-format string) to Persian date and time.

    Args:
        dt (Union[str, datetime]): datetime object or ISO-format datetime string.

    Returns:
        Tuple[str, str]: Persian date and time in string format.
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            raise ValueError(
                "Invalid datetime string format passed to persian_date_time"
            )

    tehran_time = dt.astimezone(ZoneInfo("Asia/Tehran"))
    jalali = JalaliDateTime.to_jalali(tehran_time)
    return (
        jalali.strftime("%d %B %Y", locale="fa"),
        jalali.strftime("%H:%M", locale="fa"),
    )
