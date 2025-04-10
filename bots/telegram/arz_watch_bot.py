import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes


from logger import LoggerFactory
from scrapers.alan_chand import AlanChandGoldScraper, AlanChandCoinScraper

from bots.telegram import messages
from bots.telegram.db import get_total_users, upsert_user

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
        # Create a scraper for fetching coin data
        self.coin_scraper = AlanChandCoinScraper()
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
        self.app.add_handler(CommandHandler("gold", self.handle_gold))
        self.app.add_handler(CommandHandler("coin", self.handle_coin))
        self.app.add_handler(CommandHandler("help", self.handle_help))

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the start command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        user = update.effective_user
        username = user.username or ""
        first_name = user.first_name or ""
        last_name = user.last_name or ""

        # Save user data to the database
        upsert_user(user.id, username, first_name, last_name)

        # Get the total number of users
        total_users = get_total_users()

        name_to_welcome = first_name or username

        welcome_msg = messages.welcome(name_to_welcome, total_users)

        self.logger.info(f"New user: {username} {first_name} {last_name}")

        await update.message.reply_text(welcome_msg, parse_mode="HTML")

    async def handle_gold(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the gold command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        # Get the gold data from the scraper
        gold_scraper = self.gold_scraper
        data = gold_scraper.fetch_gold_data()
        # Separate the data into different parts
        last_update = data.get("last_update", "N/A")
        time_part = last_update.split(" ")[0]
        date_part = " ".join(last_update.split(" ")[2:])
        gold_items = data.get("golds", [])
        # Check if the gold data is valid
        gram_18k = next((item for item in gold_items if "18" in item["title"]), None)
        misqal = next((item for item in gold_items if "Misqal" in item["title"]), None)

        if not gram_18k or not misqal:
            await update.message.reply_text(messages.error())
            return

        await update.message.reply_text(
            messages.gold(misqal, gram_18k, date_part, time_part), parse_mode="HTML"
        )

    async def handle_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the coin command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        # Get the coin data from the scraper
        coin_scraper = self.coin_scraper
        data = coin_scraper.fetch_coin_data()
        # Separate the data into different parts
        last_update = data.get("last_update", "N/A")
        time_part = last_update.split(" ")[0]
        date_part = " ".join(last_update.split(" ")[2:])

        coin_title_map = self.coin_scraper.get_etp_coin_title_map()

        coin_items = data.get("coins", [])
        if not coin_items:
            await update.message.reply_text(messages.error())
            return

        await update.message.reply_text(
            messages.coin(coin_items, date_part, time_part, coin_title_map),
            parse_mode="HTML",
        )

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the help command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        await update.message.reply_text(messages.help(), parse_mode="HTML")

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
            await update.message.reply_text(messages.error(), parse_mode="HTML")

    def run(self):
        """Starts the bot."""
        self.logger.info("ArzWatchBot is starting polling...")
        self.app.run_polling()
