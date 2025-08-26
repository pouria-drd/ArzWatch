from typing import Optional
from asgiref.sync import sync_to_async
from .is_valid_language import is_valid_language
from .increment_requests import increment_requests
from bot.models import TelegramUserModel, TelegramCommandModel


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
