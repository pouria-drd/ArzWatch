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
    "gold_item": {
        "fa": (
            "📊<b>{name} ({symbol})</b>\n\n"
            "💰قیمت: {price:,} {currency}\n"
            "📅<b>آخرین به روز رسانی:</b>{date} {time}\n"
            "🔗منبع: {source}\n\n"
        ),
        "en": (
            "📊<b>{name} ({symbol})</b>\n\n"
            "💰Price: {price:,} {currency}\n"
            "📅<b>Last updated:</b>{date} {time}\n"
            "🔗Source: {source}\n\n"
        ),
    },
    "coin_item": {
        "fa": (
            "📊<b>{name} ({symbol})</b>\n\n"
            "💰<b>قیمت:</b> {price:,} {currency}\n"
            "📅<b>آخرین به روز رسانی:</b>{date} {time}\n"
            "🔗منبع: {source}\n\n"
        ),
        "en": (
            "📊<b>{name} ({symbol})</b>\n\n"
            "💰<b>Price:</b> {price:,} {currency}\n"
            "📅<b>Last updated:</b>{date} {time}\n"
            "🔗Source: {source}\n\n"
        ),
    },
    "crypto_item": {
        "fa": (
            "📊<b>{name} ({symbol})</b>\n\n"
            "💰<b>قیمت:</b> {price_irr:,} ریال\n"
            "💰<b>قیمت دلاری:</b> {price:,} {currency}\n"
            "📅<b>آخرین به روز رسانی:</b>{date} {time}\n"
            "🔗منبع: {source}\n\n"
        ),
        "en": (
            "📊<b>{name} ({symbol})</b>\n\n"
            "💰<b>Price:</b> {price:,} {currency}\n"
            "💰<b>Price in IRR:</b> {price_irr:,} IRR\n"
            "📅<b>Last updated:</b>{date} {time}\n"
            "🔗Source: {source}\n\n"
        ),
    },
    "currency_item": {
        "fa": (
            "📊<b>{name} ({symbol})</b>\n\n"
            "💰<b>قیمت:</b> {price:,} {currency}\n"
            "📅<b>آخرین به روز رسانی:</b>{date} {time}\n"
            "🔗منبع: {source}\n\n"
        ),
        "en": (
            "📊<b>{name} ({symbol})</b>\n\n"
            "💰<b>Price:</b> {price:,} {currency}\n"
            "📅<b>Last updated:</b>{date} {time}\n"
            "🔗Source: {source}\n\n"
        ),
    },
    "usage": {
        "fa": (
            "خیلی خوشحالیم که از ربات ما استفاده می‌کنی <b>{name}</b>🎉\n\n"
            "اطلاعات مصرفی شما:\n\n"
            "{usage_emoji} <b>درصد مصرف:</b> <code>{percent}%</code>\n"
            "📊<b>تعداد درخواست امروز:</b> <code>{request_count}</code> از <code>{max_request_count}</code>\n"
            "🗓️تاریخ عضویت: <b>{date}</b>⏰\n\n"
            "{warning}"
        ),
        "en": (
            "We’re happy you’re using our bot, <b>{name}</b>!🎉\n\n"
            "Your usage info:\n\n"
            "{usage_emoji} <b>Usage percent:</b> <code>{percent}%</code>\n"
            "📊<b>Requests today:</b> <code>{request_count}</code> out of <code>{max_request_count}</code>\n"
            "🗓️Joined: <b>{date}</b>⏰\n\n"
            "{warning}"
        ),
    },
    "warnings": {
        "fa": {
            "100": "⛔<b>شما به سقف مجاز امروز رسیدید !</b>",
            "90": "🚨<b>شما به سقف مجاز امروز نزدیک شده‌اید!</b>",
            "70": "⚠️<b>در حال نزدیک شدن به سقف مجاز هستید.</b>",
            "ok": "",
        },
        "en": {
            "100": "⛔<b>You have reached today’s limit!</b>",
            "90": "🚨<b>You are close to today’s limit!</b>",
            "70": "⚠️<b>You are approaching the daily limit.</b>",
            "ok": "",
        },
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
        "fa": "حساب کاربری یافت نشد😕",
        "en": "User not found😕",
    },
    "user_not_active": {
        "fa": "حساب کاربری فعال نیست😕",
        "en": "User is inactive😕",
    },
    "too_many_requests": {
        "fa": "شما نمی توانید در این روز درخواست جدیدی داشته باشید😓",
        "en": "You can't make a new request today😓",
    },
    "no_data": {
        "fa": "هیچ داده‌ای یافت نشد😕",
        "en": "No data found😕",
    },
    "error": {
        "fa": "خطایی رخ داده است😕",
        "en": "An error occurred😕",
    },
}


def get_message(key: str, user=None, preferred_lang: str = "fa", **kwargs) -> str:
    """
    Returns a message based on the user's preferred language.
    Falls back to 'fa' if language is invalid or not set.
    """
    lang = preferred_lang
    if user is not None:
        lang = getattr(user, "preferred_language", preferred_lang)

    if lang not in AVAILABLE_LANGS:
        lang = "fa"  # fallback language

    msg_template = MESSAGES.get(key, {}).get(lang, "")
    return msg_template.format(**kwargs)
