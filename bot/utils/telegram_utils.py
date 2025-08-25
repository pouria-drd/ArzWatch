import logging
from typing import Optional, Union

from telegram import Update
from asgiref.sync import sync_to_async

from ..messages import telegram_messages
from ..models import TelegramUserModel, TelegramCommandModel

logger = logging.getLogger("telegram_bot")


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
                logger.warning(f"User {update.effective_user.name} exceeded daily requests.")  # type: ignore
                return {
                    "ok": False,
                    "code": "too_many_requests",
                    "tg_user": None,
                    "error": telegram_messages.get_message(
                        "too_many_requests", update.effective_user
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
                    "user_not_found", update.effective_user
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
            TelegramCommandModel.log(
                user,
                TelegramCommandModel.CommandType.START,
                f"New user {user} created.",
            )
        else:
            user.increment_requests()

            TelegramCommandModel.log(
                user,
                TelegramCommandModel.CommandType.START,
                f"User {user} already exists.",
            )

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
        tg_user.increment_requests()
        tg_user.preferred_language = lang_code
        tg_user.save()

        TelegramCommandModel.log(
            tg_user,
            TelegramCommandModel.CommandType.REQUEST,
            f"Preferred language set to {lang_code} by {tg_user}",
        )

        return tg_user

    return await change_language()
