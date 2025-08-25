from telegram import Update
from asgiref.sync import sync_to_async
from ..models import TelegramUserModel, TelegramCommandModel


async def change_language(update: Update, lang: str):
    effective_user = update.effective_user

    @sync_to_async
    def change_language():
        tg_user = TelegramUserModel.objects.get(user_id=effective_user.id)  # type: ignore
        tg_user.preferred_language = lang
        tg_user.save()

        TelegramCommandModel.log(
            tg_user,
            TelegramCommandModel.CommandType.REQUEST,
            f"Language set to {lang}",
        )

        return tg_user

    return await change_language()


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
            TelegramCommandModel.log(
                user,
                TelegramCommandModel.CommandType.START,
                f"User {user} already exists.",
            )
        return user

    return await get_or_create_user()
