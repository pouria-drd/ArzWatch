import logging
from typing import Optional

from telegram import Update
from asgiref.sync import sync_to_async

from ..utils import persian_date_time
from ..messages import telegram_messages
from ..models import TelegramUserModel, TelegramCommandModel

logger = logging.getLogger("telegram_bot")


def increment_requests(
    tg_user: TelegramUserModel, type: TelegramCommandModel.CommandType, message: str
) -> None:
    """
    Increment a user's request count and logs the event.

    Args:
        tg_user (TelegramUserModel): User object.
    """
    tg_user.increment_requests()
    TelegramCommandModel.log(tg_user, type, message)


def is_valid_language(lang_code: str) -> bool:
    """
    Validate a language code

    Args:
        lang_code (str): Language code to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return lang_code in telegram_messages.AVAILABLE_LANGS


async def get_valid_user(update: Update) -> dict:
    """
    Get a valid Telegram user from DB (async-safe).
    Always returns a dict in the following format:

        {
            "ok": bool,           # True if valid user, False otherwise
            "code": str,          # Code for success/error (too_many_requests, success, user_not_fount, unexpected_error, etc.)
            "tg_user": TelegramUserModel | None,  # TelegramUserModel instance if ok=True
            "error": str | None   # Error message string if ok=False
        }

    Args:
        update (Update): Telegram Update object.

    Returns:
        dict: Standardized result containing either the user object or error message.
    """

    @sync_to_async
    def get_valid_user():
        try:
            user_id = update.effective_user.id  # type: ignore
            tg_user = TelegramUserModel.objects.get(user_id=user_id, status="active")

            # Check if user can still make requests today
            if not tg_user.can_make_request():
                logger.warning(f"User {tg_user} exceeded daily requests.")
                return {
                    "ok": False,
                    "code": "too_many_requests",
                    "tg_user": None,
                    "error": telegram_messages.get_message(
                        "too_many_requests", tg_user
                    ),
                }

            return {
                "ok": True,
                "code": "success",
                "tg_user": tg_user,
                "error": None,
            }

        except TelegramUserModel.DoesNotExist:
            logger.warning(f"User {update.effective_user.name} not found or inactive.")  # type: ignore
            return {
                "ok": False,
                "code": "user_not_found",
                "tg_user": None,
                "error": telegram_messages.get_message(
                    "user_not_found",
                    update.effective_user,
                ),
            }

        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return {
                "ok": False,
                "code": "unexpected_error",
                "tg_user": None,
                "error": telegram_messages.get_message("error", update.effective_user),
            }

    return await get_valid_user()


async def create_user(update: Update) -> TelegramUserModel:
    """
    Create a new Telegram user (async-safe)
    """
    user_id = update.effective_user.id  # type: ignore
    effective_user = update.effective_user

    @sync_to_async
    def get_or_create_user():
        user, created = TelegramUserModel.objects.get_or_create(
            user_id=user_id,
            defaults={
                "username": effective_user.username,  # type: ignore
                "first_name": effective_user.first_name,  # type: ignore
                "last_name": effective_user.last_name,  # type: ignore
                "is_bot": bool(getattr(effective_user, "is_bot", False)),
                "is_premium": bool(getattr(effective_user, "is_premium", False)),
                "language_code": effective_user.language_code,  # type: ignore
            },
        )
        if created:
            message = f"New user {user} created."
            increment_requests(user, TelegramCommandModel.CommandType.START, message)
        else:
            message = f"User {user} already exists."
            increment_requests(user, TelegramCommandModel.CommandType.START, message)

        return user

    return await get_or_create_user()


async def change_language(
    tg_user: TelegramUserModel, lang_code: str
) -> Optional[TelegramUserModel]:
    """
    Change the preferred language of a Telegram user (async-safe).

    Args:
        update (Update): Telegram Update object.
        lang_code (str): Language code to change to.

    Returns:
        TelegramUserModel | None: Updated user object if successful, None otherwise.
    """

    if not is_valid_language(lang_code):
        return None

    @sync_to_async
    def change_language():
        tg_user.preferred_language = lang_code
        tg_user.save()

        message = f"Preferred language set to {lang_code} by {tg_user}"
        increment_requests(tg_user, TelegramCommandModel.CommandType.REQUEST, message)

        return tg_user

    return await change_language()


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
