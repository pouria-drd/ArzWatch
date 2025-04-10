from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from scrapers.alan_chand import AlanChandGoldScraper, AlanChandCoinScraper

# Initialize the scrapers
gold_scraper = AlanChandGoldScraper()
coin_scraper = AlanChandCoinScraper()

# Initialize the cached data
cached_data = {"gold": None, "coin": None, "last_updated": None}


def fetch_and_cache_data():
    """Fetches and caches data from the scrapers."""
    cached_data["gold"] = gold_scraper.fetch_gold_data()
    cached_data["coin"] = coin_scraper.fetch_coin_data()
    now = datetime.now(timezone.utc).isoformat()
    cached_data["last_updated"] = now


# schedule the tasks to run every 3 minutes
def start_scheduler():
    """Starts the scheduler to run the fetch_and_cache_data function every 3 minutes."""
    scheduler = BackgroundScheduler()
    # Run every 3 minutes
    scheduler.add_job(fetch_and_cache_data, "interval", minutes=3)
    scheduler.start()


# Call the function to fetch and cache data
fetch_and_cache_data()

# Start the scheduler
start_scheduler()


def get_gold_price():
    """Get the gold price from the cache"""
    return cached_data["gold"]


def get_coin_price():
    """Get the coin price from the cache"""
    return cached_data["coin"]


def get_last_updated():
    """ "Get the last updated time from the cache"""
    return cached_data["last_updated"]
