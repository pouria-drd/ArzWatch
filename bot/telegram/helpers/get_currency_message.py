from bot.messages import get_message
from asgiref.sync import sync_to_async
from bot.utils import persian_date_time
from .increment_requests import increment_requests
from bot.models import TelegramUserModel, TelegramCommandModel


async def get_currency_message(tg_user: TelegramUserModel, query_result: dict) -> str:
    if not query_result or "results" not in query_result:
        return get_message(key="no_data", user=tg_user)

    messages = []
    instruments = query_result["results"]
    user_lang = getattr(tg_user, "preferred_language", "fa")

    for inst in instruments:
        symbol = inst.get("symbol", "-")
        latest = inst.get("latestPriceTick", {})
        meta = latest.get("meta", {})
        price = latest.get("price")
        currency = latest.get("currency", "")
        source = meta.get("source_url", "")
        timestamp = latest.get("timestamp", "")

        if user_lang == "en":
            name = inst.get("name", "-")
            date = timestamp.strftime("%Y-%m-%d")  # type: ignore
            time = timestamp.strftime("%H:%M")  # type: ignore
        else:
            name = inst.get("faName", "-")
            date, time = persian_date_time(timestamp)

        msg = get_message(
            key="currency_item",
            user=tg_user,
            name=name,
            price=price,
            symbol=symbol,
            currency=currency,
            date=date,
            time=time,
            source=source,
        )

        messages.append(msg)

    # Log and increment request count
    @sync_to_async
    def log_request():
        increment_requests(
            tg_user,
            TelegramCommandModel.CommandType.REQUEST,
            f"{tg_user} requested currency info.",
        )

    await log_request()

    return "\n\n".join(messages)
