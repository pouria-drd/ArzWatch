from datetime import datetime, timezone
from extractors.tgju import TGJUCoinExtractor, TGJUGoldExtractor


# Initialize the scrapers
tgju_coin_extractor = TGJUCoinExtractor()
tgju_gold_extractor = TGJUGoldExtractor()


# Initialize the cached data
cached_data = {"gold": None, "coin": None, "last_updated": None}


def get_gold_price():
    """Get the gold price from the cache"""
    return cached_data["gold"]
    # return gold_extractor.fetch_data()


def get_coin_price():
    """Get the coin price from the cache"""
    return cached_data["coin"]
    # return coin_extractor.fetch_data()


def get_last_updated():
    """ "Get the last updated time from the cache"""
    return cached_data["last_updated"]


def fetch_and_cache_data():
    """Fetches and caches data from the scrapers."""

    # Set the last updated time to now
    now = datetime.now(timezone.utc).isoformat()
    cached_data["last_updated"] = now

    # Fetch TGJU coin data
    tgju_coin_data = tgju_coin_extractor.fetch_data()
    if tgju_coin_data:
        cached_data["coin"] = tgju_coin_data

    # Fetch TGJU gold data
    tgju_gold_data = tgju_gold_extractor.fetch_data()
    if tgju_gold_data:
        cached_data["gold"] = tgju_gold_data
