import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes

from logger import LoggerFactory
from scrapers.alan_chand import AlanChandGoldScraper, AlanChandCoinScraper

# Enable logging for debugging and monitoring
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class ArzWatchBot:
    """
    ArzWatchBot is a Telegram bot that sends real-time currency and price updates.
    """

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Get the Telegram bot token from the .env file
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        # Check if the token is not empty
        if not self.token:
            # Raise an exception with a message
            raise ValueError("❌ Telegram bot token not found in .env file!")
        # Create a logger for the bot
        self.logger = LoggerFactory.get_logger(
            "ArzWatchBot", "bots/telegram/arz_watch_bot"
        )
        # Create a Telegram bot
        self.app: Application = ApplicationBuilder().token(self.token).build()
        # Create a scraper for fetching gold data
        self.gold_scraper = AlanChandGoldScraper()
        # Register handlers
        self.register_handlers()
        # Register error handler
        self.app.add_error_handler(self.handle_error)

    def register_handlers(self):
        """
        Registers the handlers for the Telegram bot.
        """
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.handle_start))
        # self.app.add_handler(CommandHandler("gold", self.handle_gold))
        # self.app.add_handler(CommandHandler("coin", self.handle_coin))
        self.app.add_handler(CommandHandler("help", self.handle_help))

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the start command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        user = update.effective_user
        username = f"{user.first_name}" if user.first_name else user.username

        await update.message.reply_text(
            f"""
سلام 👋 <b>{username}</b> عزیز!  
به ربات <b>ArzWatch</b> خوش اومدی 🟢

این ربات برای نمایش قیمت‌های لحظه‌ای بازار طراحی شده 🧠

برای مشاهده دستورات موجود، کافیه از دستور زیر استفاده کنی:
👉 <b>/help</b>
""",
            parse_mode="HTML",
        )

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the help command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        await update.message.reply_text(
            """
/gold - قیمت طلا
/coin - قیمت سکه
/help - راهنما
"""
        )

    async def handle_error(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles errors that occur during the bot's operation.

        Args:
            update (object): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        # Log the error
        self.logger.error("Unhandled error occurred", exc_info=context.error)
        # Reply to the user with an error message
        if isinstance(update, Update) and update.message:
            await update.message.reply_text("❌ خطای داخلی. لطفا دوباره امتحان کن.")

    def run(self):
        """Starts the bot."""
        self.logger.info("ArzWatchBot is starting polling...")
        self.app.run_polling()
