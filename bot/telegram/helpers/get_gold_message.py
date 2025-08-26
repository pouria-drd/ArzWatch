from bot.messages import get_message
from asgiref.sync import sync_to_async
from bot.utils import persian_date_time
from .increment_requests import increment_requests
from bot.models import TelegramUserModel, TelegramCommandModel


async def get_gold_message(
    tg_user: TelegramUserModel, query_result: dict, lang: str = "fa"
) -> str:
    if not query_result or "results" not in query_result:
        return get_message("no_data", preferred_lang=lang)

    instruments = query_result["results"]
    messages = []

    for inst in instruments:
        name = inst.get("name", "-")
        fa_name = inst.get("faName", "-")
        symbol = inst.get("symbol", "-")
        latest = inst.get("latestPriceTick", {})
        price = latest.get("price", "-")
        currency = latest.get("currency", "")
        meta = latest.get("meta", {})
        source = meta.get("source_url", "")
        timestamp = latest.get("timestamp", "")

        if lang == "en":
            date = timestamp.strftime("%Y-%m-%d %H:%M:")
            msg = get_message(
                "gold_item",
                preferred_lang=lang,
                name=name,
                symbol=symbol,
                price=price,
                currency=currency,
                date=date,
                source=source,
            )
        else:
            date, time = persian_date_time(timestamp)
            msg = get_message(
                "gold_item",
                preferred_lang=lang,
                name=fa_name,
                symbol=symbol,
                price=price,
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
            f"{tg_user} requested gold info.",
        )

    await log_request()

    return "\n\n".join(messages)
