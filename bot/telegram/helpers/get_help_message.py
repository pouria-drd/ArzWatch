from bot.messages import get_message
from asgiref.sync import sync_to_async
from bot.utils import persian_date_time
from .increment_requests import increment_requests
from bot.models import TelegramUserModel, TelegramCommandModel


async def get_help_message(tg_user: TelegramUserModel) -> str:
    """
    Generates a message for the /help command.
    """

    msg = get_message(
        key="help",
        user=tg_user,
    )

    # Log and increment request count
    @sync_to_async
    def log_request():
        increment_requests(
            tg_user,
            TelegramCommandModel.CommandType.REQUEST,
            f"{tg_user} requested help info.",
        )

    await log_request()

    return msg
