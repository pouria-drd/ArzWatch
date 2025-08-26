import logging
from telegram import Update
from asgiref.sync import sync_to_async
from .increment_requests import increment_requests
from bot.models import TelegramUserModel, TelegramCommandModel

logger = logging.getLogger("telegram_bot")


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
            logger.info(message)
            increment_requests(user, TelegramCommandModel.CommandType.START, message)
        else:
            message = f"User {user} already exists."
            logger.info(message)
            increment_requests(user, TelegramCommandModel.CommandType.START, message)

        return user

    return await get_or_create_user()
