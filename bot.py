import os
from dotenv import load_dotenv


from bots.telegram import ArzWatchBot


# Load environment variables from .env file
load_dotenv()

BASE_API_URL = os.getenv("BASE_API_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def main():
    bot = ArzWatchBot(BASE_API_URL, TELEGRAM_BOT_TOKEN)
    bot.run()


if __name__ == "__main__":
    main()
