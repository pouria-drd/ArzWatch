from asgiref.sync import sync_to_async
from bot.models import TelegramCommandModel
from bot.utils.utils import persian_date_time
from .increment_requests import increment_requests


async def generate_usage_message(
    tg_user,
    request_count,
    max_request_count,
    created_at,
    lang: str = "fa",
) -> str:
    """
    Generate a usage summary message for a Telegram user.

    Args:
        user: Telegram user object (with .first_name or .name)
        request_count: Current request count for the day
        max_request_count: Maximum allowed request count
        created_at: Datetime of account creation
        lang: Preferred language ("fa" or "en")

    Returns:
        str: A formatted multilingual message (HTML-ready)
    """
    name = f"{tg_user}"

    # Normalize counts
    request_count = int(request_count)
    max_request_count = int(max_request_count)
    percent = int((request_count / max_request_count) * 100)

    # Emoji indicator based on usage level
    if percent < 40:
        usage_emoji = "🟢"
    elif percent < 70:
        usage_emoji = "🟡"
    elif percent < 90:
        usage_emoji = "🟠"
    else:
        usage_emoji = "🔴"

    # Warning message (per language)
    warnings = {
        "fa": {
            "100": "⛔ <b>شما به سقف مجاز امروز رسیدید !</b>",
            "90": "🚨 <b>شما به سقف مجاز امروز نزدیک شده‌اید!</b>",
            "70": "⚠️ <b>در حال نزدیک شدن به سقف مجاز هستید.</b>",
            "ok": "",
        },
        "en": {
            "100": "⛔ <b>You have reached today’s limit!</b>",
            "90": "🚨 <b>You are close to today’s limit!</b>",
            "70": "⚠️ <b>You are approaching the daily limit.</b>",
            "ok": "",
        },
    }

    if percent >= 100:
        warning = warnings[lang]["100"]
    elif percent >= 90:
        warning = warnings[lang]["90"]
    elif percent >= 70:
        warning = warnings[lang]["70"]
    else:
        warning = warnings[lang]["ok"]

    # Date formatting
    if lang == "fa":
        persian_date, persian_time = persian_date_time(created_at)
        message = f"""
خیلی خوشحالیم که از ربات ما استفاده می‌کنی <b>{name}</b>🎉

اطلاعات مصرفی شما:

{usage_emoji} <b>درصد مصرف:</b> <code>{percent}%</code>
📊 <b>تعداد درخواست امروز:</b> <code>{request_count}</code> از <code>{max_request_count}</code>
🗓️ تاریخ عضویت: <b>{persian_date}</b>⏰

{warning}
"""
    else:  # English
        date_str = created_at.strftime("%Y-%m-%d")
        time_str = created_at.strftime("%H:%M:%S")
        message = f"""
We’re happy you’re using our bot, <b>{name}</b>!🎉

Your usage info:

{usage_emoji} <b>Usage percent:</b> <code>{percent}%</code>
📊 <b>Requests today:</b> <code>{request_count}</code> out of <code>{max_request_count}</code>
🗓️ Joined: <b>{date_str}</b>⏰

{warning}
"""

    # Update user usage info
    @sync_to_async
    def update_user():
        msg = f"{tg_user} requested usage info."
        increment_requests(tg_user, TelegramCommandModel.CommandType.REQUEST, msg)

    await update_user()

    return message.strip()
