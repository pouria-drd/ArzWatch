from bot.messages.telegram_messages import AVAILABLE_LANGS


def is_valid_language(lang_code: str) -> bool:
    """
    Validate a language code

    Args:
        lang_code (str): Language code to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return lang_code in AVAILABLE_LANGS
