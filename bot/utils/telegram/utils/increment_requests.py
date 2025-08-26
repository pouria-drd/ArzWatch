from bot.models import TelegramUserModel, TelegramCommandModel


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
