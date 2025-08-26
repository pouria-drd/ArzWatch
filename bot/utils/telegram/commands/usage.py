import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.telegram.utils import get_valid_user, generate_usage_message

logger = logging.getLogger("telegram_bot")


async def usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /usage command for a Telegram user.
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
    # Build usage message
    message = await generate_usage_message(
        tg_user=tg_user,
        request_count=tg_user.requests,
        max_request_count=tg_user.max_requests,
        created_at=tg_user.created_at,
        lang=lang,
    )
    # Successful update → log and reply
    logger.info(f"{tg_user} requested usage info.")
    await update.message.reply_text(  # type: ignore
        text=message,
        parse_mode="HTML",
        reply_to_message_id=update.message.message_id,  # type: ignore
    )
