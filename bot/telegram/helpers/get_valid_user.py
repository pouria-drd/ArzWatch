import logging
from telegram import Update
from asgiref.sync import sync_to_async

from bot.messages import get_message
from bot.models import TelegramUserModel

logger = logging.getLogger("telegram_bot")


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
            tg_user = TelegramUserModel.objects.get(user_id=user_id)

            if not tg_user.status == "active":
                logger.warning(f"User {tg_user} is not active: status={tg_user.status}")
                return {
                    "ok": False,
                    "code": "user_not_active",
                    "tg_user": None,
                    "error": get_message("user_not_active", tg_user),
                }

            # Check if user can still make requests today
            if not tg_user.can_make_request():
                logger.warning(f"User {tg_user} exceeded daily requests.")
                return {
                    "ok": False,
                    "code": "too_many_requests",
                    "tg_user": None,
                    "error": get_message("too_many_requests", tg_user),
                }

            return {
                "ok": True,
                "code": "success",
                "tg_user": tg_user,
                "error": None,
            }

        except TelegramUserModel.DoesNotExist:
            logger.warning(f"User {update.effective_user.name} not found.")  # type: ignore
            return {
                "ok": False,
                "code": "user_not_found",
                "tg_user": None,
                "error": get_message(
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
                "error": get_message("error", update.effective_user),
            }

    return await get_valid_user()
