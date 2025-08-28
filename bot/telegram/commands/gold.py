import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..helpers import get_valid_user, get_gold_message, fetch_instruments

logger = logging.getLogger("telegram_bot")


async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /gold command for a Telegram user.
    """
    # Get user result
    result = await get_valid_user(update)
    # Check if user is valid
    if not result["ok"]:
        # User invalid → reply with error and exit
        await update.message.reply_text(  # type: ignore
            text=result["error"],
            reply_to_message_id=update.message.message_id,  # type: ignore
            parse_mode="HTML",
        )
        return
    # Valid user → extract info
    tg_user = result["tg_user"]
    lang = getattr(tg_user, "preferred_language", "fa")
    # Fetch instruments
    query_result = await fetch_instruments(category="gold")
    # Build gold message
    message = await get_gold_message(tg_user=tg_user, query_result=query_result)
    # Successful update → log and reply
    logger.info(f"{tg_user} requested gold info.")
    await update.message.reply_text(  # type: ignore
        text=message,
        parse_mode="HTML",
        reply_to_message_id=update.message.message_id,  # type: ignore
    )
