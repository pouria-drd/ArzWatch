from api.services.tgju.price_fetcher import fetch_and_cache_data
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize the scheduler
scheduler = BackgroundScheduler()


def start_scheduler(minutes: int = 5):
    """Starts the scheduler to run the fetch_and_cache_data function every 5 minutes by default."""
    # Initial fetch to populate the cache
    fetch_and_cache_data()
    # Run every 5 minutes by default
    scheduler.add_job(fetch_and_cache_data, "interval", minutes=minutes)
    scheduler.start()


def stop_scheduler():
    """Stops the scheduler."""
    # Shutdown the scheduler
    scheduler.shutdown()
