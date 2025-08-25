import logging
from . import telegram_utils
from ..messages import telegram_messages

from telegram import Update
from telegram.ext import ContextTypes


logger = logging.getLogger("telegram_bot")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Get user result
    result = await telegram_utils.get_valid_user(update)
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
    tg_user = await telegram_utils.create_user(update)
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


async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /setlang command for a Telegram user.
    """

    effective_user = update.effective_user
    effective_user_name = effective_user.name  # type: ignore
    # Get user result
    result = await telegram_utils.get_valid_user(update)
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
    updated_user = await telegram_utils.change_language(tg_user, lang)
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
