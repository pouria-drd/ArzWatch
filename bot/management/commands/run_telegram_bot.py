import logging
from ...utils import telegram_utils
from ...messages import telegram_messages

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from django.conf import settings
from django.core.management.base import BaseCommand


logger = logging.getLogger("telegram_bot")


class Command(BaseCommand):
    help = "Run the Telegram bot for ArzWatch"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Telegram bot..."))
        try:
            # Initialize the application builder
            builder = Application.builder().token(settings.TELEGRAM_BOT_TOKEN)

            # Configure proxy if TELEGRAM_PROXY_URL is set
            if settings.TELEGRAM_PROXY_URL:
                builder.proxy(settings.TELEGRAM_PROXY_URL)
                builder.get_updates_proxy(settings.TELEGRAM_PROXY_URL)
                logger.info("Using proxy for Telegram bot.")

            # Build the application
            builder.get_updates_connect_timeout(10)
            builder.get_updates_read_timeout(10)
            builder.get_updates_write_timeout(10)
            builder.get_updates_pool_timeout(10)

            application = builder.build()

            # Add command handler
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("set_lang", set_language))

            # Start the bot
            logger.info("Bot started!")
            self.stdout.write(self.style.SUCCESS("Bot started!"))
            application.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Error running bot: {str(e)}"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create a new Telegram user
    tg_user = await telegram_utils.create_user(update)
    tg_user_name = f"{tg_user}"
    # Log the user
    logger.info(f"User {tg_user_name} accessed start command.")
    # Send welcome message
    msg = telegram_messages.get_message("welcome", tg_user, name=tg_user_name)
    await update.message.reply_text(msg, parse_mode="HTML")  # type: ignore


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get language code from context
    lang = context.args[0] if context.args else "fa"
    # Validate language code
    if lang not in telegram_messages.AVAILABLE_LANGS:
        await update.message.reply_text(  # type: ignore
            telegram_messages.get_message("invalid_lang", update.effective_user.name),  # type: ignore
        )
        return
    # Change language
    tg_user = await telegram_utils.change_language(update, lang)
    # Log the user
    logger.info(f"User {tg_user} changed language to {lang}.")
    # Send success message
    await update.message.reply_text(telegram_messages.get_message("set_lang_success", tg_user))  # type: ignore
