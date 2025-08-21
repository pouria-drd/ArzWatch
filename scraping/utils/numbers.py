from typing import Optional
from decimal import Decimal, InvalidOperation

from .text import normalize_digits, strip_commas, extract_first_number


def to_decimal(s: str) -> Decimal:
    """
    Convert a price-like string into Decimal:
    - normalizes Persian/Arabic numerals
    - removes common decorations like commas, currency symbols (caller should pre-strip $/ریال if needed)
    """
    raw = normalize_digits(strip_commas(s)).strip()
    try:
        return Decimal(raw)
    except InvalidOperation:
        # last try: attempt to extract a number
        num = extract_first_number(raw)
        if num is None:
            raise
        return Decimal(num)


def try_decimal(s: str) -> Optional[Decimal]:
    """Safe Decimal parse; returns None if invalid."""
    try:
        return to_decimal(s)
    except Exception:
        return None
