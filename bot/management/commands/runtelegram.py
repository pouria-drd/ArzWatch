import logging
from telegram import Update
from telegram.ext import Application, CommandHandler

from django.conf import settings
from django.core.management.base import BaseCommand

from bot.telegram.commands import start, usage, set_lang

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

            # Register command handlers
            application.add_handlers(
                [
                    # General commands
                    CommandHandler("start", start),
                    CommandHandler("usage", usage),
                    CommandHandler("setlang", set_lang),
                    # Instruments commands
                    # CommandHandler("gold", gold),
                    # CommandHandler("coin", coin),
                    # CommandHandler("crypto", crypto),
                    # CommandHandler("currency", currency),
                ]
            )

            # Start the bot
            logger.info("Bot started!")
            self.stdout.write(self.style.SUCCESS("Bot started!"))
            application.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Error running bot: {str(e)}"))
