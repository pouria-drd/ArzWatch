import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.messages import telegram_messages
from ..helpers import get_valid_user, change_language

logger = logging.getLogger("telegram_bot")


async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /setlang command for a Telegram user.
    """
    # Get effective user data
    effective_user = update.effective_user
    effective_user_name = effective_user.name  # type: ignore
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
    # User valid → extract user
    tg_user = result["tg_user"]
    # Extract lang code (default = fa)
    lang = context.args[0].strip().lower() if context.args else "fa"
    # Try to update language
    updated_user = await change_language(tg_user, lang)
    # Check if language is invalid
    if updated_user is None:
        await update.message.reply_text(  # type: ignore
            text=telegram_messages.get_message("invalid_lang", tg_user),
            reply_to_message_id=update.message.message_id,  # type: ignore
            parse_mode="HTML",
        )
        logger.warning(f"{effective_user_name} tried to set invalid language: {lang}")
        return
    # Successful update → log and reply
    logger.info(f"{updated_user} changed preferred language to: {lang}")
    await update.message.reply_text(  # type: ignore
        text=telegram_messages.get_message("set_lang_success", updated_user),
        reply_to_message_id=update.message.message_id,  # type: ignore
        parse_mode="HTML",
    )
