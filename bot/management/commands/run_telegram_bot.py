import logging
from ...messages import welcome
from django.conf import settings

from telegram import Update
from telegram.request import HTTPXRequest
from django.core.management.base import BaseCommand
from telegram.ext import Application, CommandHandler, ContextTypes


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
                logger.info(f"Using proxy: {settings.TELEGRAM_PROXY_URL}")

            # Build the application
            builder.get_updates_connect_timeout(30)
            builder.get_updates_read_timeout(30)
            builder.get_updates_write_timeout(30)
            builder.get_updates_pool_timeout(30)

            application = builder.build()

            # Add command handler
            application.add_handler(CommandHandler("start", start))

            # Start the bot
            logger.info("Bot started!")
            self.stdout.write(self.style.SUCCESS("Bot started!"))
            application.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Error running bot: {str(e)}"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    """
    logger.info(f"User {update.effective_user.name} accessed start command.")  # type: ignore
    await update.message.reply_text(welcome(update.effective_user.name), parse_mode="HTML")  # type: ignore
