import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.messages import telegram_messages
from ..helpers import get_valid_user, create_user


logger = logging.getLogger("telegram_bot")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command for a Telegram user.
    """
    # Get user result
    result = await get_valid_user(update)
    # Check if result is not ok
    if not result["ok"]:
        if (
            result["code"] == "too_many_requests"
            or result["code"] == "unexpected_error"
            or result["code"] == "user_not_found"
        ):
            # User invalid → reply with error and exit
            await update.message.reply_text(  # type: ignore
                text=result["error"],
                reply_to_message_id=update.message.message_id,  # type: ignore
                parse_mode="HTML",
            )
            return

    # Create a new Telegram user
    tg_user = await create_user(update)
    tg_user_name = f"{tg_user}"
    # Log the user
    logger.info(f"User {tg_user_name} accessed /start command.")
    # Send welcome message
    msg = telegram_messages.get_message("welcome", tg_user, name=tg_user_name)
    await update.message.reply_text(  # type: ignore
        text=msg,
        reply_to_message_id=update.message.message_id,  # type: ignore
        parse_mode="HTML",
    )
