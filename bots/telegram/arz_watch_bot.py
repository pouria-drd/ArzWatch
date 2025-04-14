import logging
import requests
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes

from logger import LoggerFactory
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

    def __init__(self, base_api_url: str, token: str, extractor: str = "tgju"):
        # Check if the BASE_API_URL is not empty
        if not base_api_url:
            # Raise an exception with a message
            raise ValueError("❌ BASE_API_URL not found in .env file!")

        # Check if the token is not empty
        if not token:
            # Raise an exception with a message
            raise ValueError("❌ Telegram bot token not found in .env file!")

        self.token = token
        # Set the extractor
        self.extractor = extractor
        # Create a base API URL
        self.base_api_url = base_api_url
        # Create a logger for the bot
        self.logger = LoggerFactory.get_logger(
            "ArzWatchBot", "bots/telegram/arz_watch_bot"
        )
        # Create a Telegram bot
        self.app: Application = ApplicationBuilder().token(self.token).build()

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
        self.app.add_handler(CommandHandler("help", self.handle_help))
        self.app.add_handler(CommandHandler("gold", self.handle_gold))
        self.app.add_handler(CommandHandler("coin", self.handle_coin))
        # self.app.add_handler(CommandHandler("crypto", self.handle_crypto))
        self.app.add_handler(CommandHandler("currency", self.handle_currency))

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

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the help command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        await update.message.reply_text(messages.help(), parse_mode="HTML")

    async def handle_gold(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the gold command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        # Get the gold data from the api
        api_url = self.base_api_url + f"/{self.extractor}/prices/gold/"
        response = requests.get(api_url, timeout=7)
        # Check if the response is not 200
        if response.status_code != 200:
            # Reply with an error message
            await update.message.reply_text(messages.error())
            return

        data = response.json()

        # Extract the last update time and format it
        last_updated = datetime.fromisoformat(
            data.get("data", {}).get("last_updated", "N/A")
        )

        gold_items = data.get("data", {}).get("golds", [])

        # Check if the gold data is valid
        if not gold_items:
            await update.message.reply_text(messages.error())
            return

        await update.message.reply_text(
            messages.gold(gold_items, last_updated), parse_mode="HTML"
        )

    async def handle_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the coin command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        # Get the coin data from the api
        api_url = self.base_api_url + f"/{self.extractor}/prices/coin/"
        response = requests.get(api_url, timeout=7)
        # Check if the response is not 200
        if response.status_code != 200:
            # Reply with an error message
            await update.message.reply_text(messages.error())
            return

        data = response.json()

        # Extract the last update time and format it
        last_updated = datetime.fromisoformat(
            data.get("data", {}).get("last_updated", "N/A")
        )

        coin_items = data.get("data", {}).get("coins", [])

        if not coin_items:
            await update.message.reply_text(messages.error())
            return

        await update.message.reply_text(
            messages.coin(coin_items, last_updated),
            parse_mode="HTML",
        )

    async def handle_currency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the currency command.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.
        """
        # Get the currency data from the api
        api_url = self.base_api_url + f"/{self.extractor}/prices/currency/"
        response = requests.get(api_url, timeout=7)
        # Check if the response is not 200
        if response.status_code != 200:
            # Reply with an error message
            await update.message.reply_text(messages.error())
            return

        data = response.json()

        # Extract the last update time and format it
        last_updated = datetime.fromisoformat(
            data.get("data", {}).get("last_updated", "N/A")
        )

        currency_items = data.get("data", {}).get("currencies", [])

        if not currency_items:
            await update.message.reply_text(messages.error())
            return

        await update.message.reply_text(
            messages.currency(currency_items, last_updated),
            parse_mode="HTML",
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
            await update.message.reply_text(messages.error(), parse_mode="HTML")

    def run(self):
        """Starts the bot."""
        self.logger.info("ArzWatchBot is starting polling...")
        self.app.run_polling()
