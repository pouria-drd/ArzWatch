import re

# Persian/Arabic digits (U+06F0..U+06F9 and U+0660..U+0669) + Arabic percent U+066A
_PERSIAN_ARABIC_DIGITS = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩"
_ASCII_DIGITS = "01234567890123456789"
_ARABIC_PERCENT = "٪"
_ASCII_PERCENT = "%"

_TRANS_TABLE = str.maketrans(
    _PERSIAN_ARABIC_DIGITS + _ARABIC_PERCENT, _ASCII_DIGITS + _ASCII_PERCENT
)


def normalize_digits(s: str) -> str:
    """
    Convert Persian/Arabic numerals and Arabic percent to ASCII.
    Leaves other characters intact.
    """
    return s.translate(_TRANS_TABLE)


def normalize_percent(s: str) -> str:
    """
    Normalize any percent sign to ASCII '%' and strip surrounding spaces.
    """
    s = normalize_digits(s)
    return s.replace(_ARABIC_PERCENT, _ASCII_PERCENT).replace(" %", "%").strip()


def strip_commas(s: str) -> str:
    """Remove thousands separators (commas) commonly used in prices."""
    return s.replace(",", "")


_NUMBER_RE = re.compile(r"([+-]?\d+(?:[\.,]\d+)?)")


def extract_first_number(s: str) -> str | None:
    """
    Find the first number in a string (accepts '.' or ',' as decimal separator),
    return it with '.' as decimal separator.
    """
    m = _NUMBER_RE.search(normalize_digits(s))
    if not m:
        return None
    return m.group(1).replace(",", ".")
