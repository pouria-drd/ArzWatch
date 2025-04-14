from bots.telegram import ArzWatchBot
from core.settings import BASE_API_URL, TELEGRAM_BOT_TOKEN


def main():
    if not BASE_API_URL or not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "BASE_API_URL and TELEGRAM_BOT_TOKEN must be set in environment variables."
        )

    bot = ArzWatchBot(BASE_API_URL, TELEGRAM_BOT_TOKEN)
    bot.run()


if __name__ == "__main__":
    main()
