from asgiref.sync import sync_to_async
from bot.utils import persian_date_time
from bot.messages import get_message, MESSAGES
from .increment_requests import increment_requests
from bot.models import TelegramUserModel, TelegramCommandModel


async def get_usage_message(
    tg_user: TelegramUserModel,
    request_count: int,
    max_request_count: int,
    created_at,
    lang: str = "fa",
) -> str:
    """
    Generate a usage status message for a Telegram user.

    Args:
        tg_user (TelegramUserModel): The Telegram user instance.
        request_count (int): Current number of requests the user made today.
        max_request_count (int): Maximum allowed requests per day.
        created_at (datetime): The user's account creation or request timestamp.
        lang (str, optional): Preferred language for the message. Defaults to "fa".

    Returns:
        str: A formatted message string with usage info.
    """

    # Normalize counts
    request_count = int(request_count)
    max_request_count = int(max_request_count)
    percent = (
        int((request_count / max_request_count) * 100) if max_request_count > 0 else 0
    )

    # Pick emoji based on usage
    if percent < 40:
        usage_emoji = "🟢"
    elif percent < 70:
        usage_emoji = "🟡"
    elif percent < 90:
        usage_emoji = "🟠"
    else:
        usage_emoji = "🔴"

    # Warning messages
    if percent >= 100:
        warning = MESSAGES["warnings"][lang]["100"]
    elif percent >= 90:
        warning = MESSAGES["warnings"][lang]["90"]
    elif percent >= 70:
        warning = MESSAGES["warnings"][lang]["70"]
    else:
        warning = MESSAGES["warnings"][lang]["ok"]

    # Date formatting
    if lang == "fa":
        date, _ = persian_date_time(created_at)
    else:
        date = created_at.strftime("%Y-%m-%d")

    # Render final message
    message = get_message(
        "usage",
        preferred_lang=lang,
        name=f"{tg_user}",
        usage_emoji=usage_emoji,
        percent=percent,
        request_count=request_count,
        max_request_count=max_request_count,
        date=date,
        warning=warning,
    )

    # Log and increment request count
    @sync_to_async
    def log_request():
        increment_requests(
            tg_user,
            TelegramCommandModel.CommandType.REQUEST,
            f"{tg_user} requested usage info.",
        )

    await log_request()

    return message
