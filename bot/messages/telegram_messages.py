AVAILABLE_LANGS = {
    "fa": "فارسی",
    "en": "English",
}

MESSAGES = {
    "welcome": {
        "fa": (
            "سلام 👋 <b>{name}</b> عزیز!\n"
            "به ربات <b>ArzWatch</b> خوش اومدی 🔥\n\n"
            "این ربات برای نمایش قیمت‌های لحظه‌ای بازار طراحی شده 🧑‍💻\n"
            "برای مشاهده دستورات: /help\n\n"
            "برای انتقادات، پیشنهادات یا گزارش باگ، لطفاً به این آیدی پیام دهید:\n"
            "@pouria_drd"
        ),
        "en": (
            "Hi dear <b>{name}</b>👋\n"
            "Welcome to <b>ArzWatch bot</b>🔥\n\n"
            "This bot is for displaying price charts 🧑‍💻\n"
            "To see available commands: /help\n\n"
            "For feedback, suggestions, or bug reports, please contact:\n"
            "@pouria_drd"
        ),
    },
    "set_lang_success": {
        "fa": "زبان شما تنظیم شد ✅",
        "en": "Your language has been set ✅",
    },
    "invalid_lang": {
        "fa": "لطفا یک کد زبان معتبر وارد کنید:\n"
        + "\n".join(
            [f"<code>/setlang {code}</code>" for code in AVAILABLE_LANGS.keys()]
        ),
        "en": "Please provide a valid language code:\n"
        + "\n".join(
            [f"<code>/setlang {code}</code>" for code in AVAILABLE_LANGS.keys()]
        ),
    },
    "user_not_found": {
        "fa": "حساب کاربری یافت نشد و یا حساب کاربری فعال نیست 😕",
        "en": "User not found or account is inactive 😕",
    },
    "too_many_requests": {
        "fa": "شما نمی توانید در این روز درخواست جدیدی داشته باشید😓",
        "en": "You can't make a new request today 😓",
    },
    "error": {
        "fa": "خطایی رخ داده است 😕",
        "en": "An error occurred 😕",
    },
}


def get_message(key: str, user, **kwargs) -> str:
    """
    Returns a message based on the user's preferred language.
    Falls back to 'fa' if language is invalid or not set.
    """
    lang = getattr(user, "preferred_language", "fa")
    if lang not in AVAILABLE_LANGS:
        lang = "fa"  # fallback language

    msg_template = MESSAGES.get(key, {}).get(lang, "")
    return msg_template.format(**kwargs)
