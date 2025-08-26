from bot.messages import get_message
from bot.utils import persian_date_time


async def get_gold_message(query_result: dict, lang: str = "fa") -> str:
    if not query_result or "results" not in query_result:
        return get_message("no_data", preferred_lang=lang)

    instruments = query_result["results"]
    messages = []

    for inst in instruments:
        name = inst.get("name", "-")
        fa_name = inst.get("fa_name", "-")
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

    return "\n\n".join(messages)
