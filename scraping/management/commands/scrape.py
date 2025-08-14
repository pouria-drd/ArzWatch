import logging
from ...models import SourceModel
from scraping.sources import TgjuScraper
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrape price data from a source with optional instruments. Example: python manage.py scrape tgju usd"

    def add_arguments(self, parser):
        parser.add_argument(
            "source", type=str, help="Source to scrape (e.g., 'tgju', 'alanchand')"
        )
        parser.add_argument(
            "instruments",
            nargs="*",
            type=str,
            help="Instruments to scrape (e.g., 'usd', 'eur'). If omitted, scrape all available instruments.",
        )

    def handle(self, *args, **options):
        source_name = options["source"].lower()
        instruments = options["instruments"]

        # Map sources to scraper classes
        scraper_map = {
            "tgju": TgjuScraper,
            "alanchand": TgjuScraper,  # Placeholder for future implementation
        }

        scraper_class = scraper_map.get(source_name)
        if not scraper_class:
            raise CommandError(
                f"No scraper defined for source '{source_name}'. Supported sources: {list(scraper_map.keys())}"
            )

        try:
            source = SourceModel.objects.get(name__iexact=source_name, enabled=True)
        except SourceModel.DoesNotExist:
            raise CommandError(f"Source '{source_name}' not found or disabled")

        try:
            self.stdout.write(
                f"Scraping {source_name} for instruments: {instruments or 'all'}..."
            )
            scraper = scraper_class(source, auto_driver=False, instruments=instruments)
            scraper.scrape()
            self.stdout.write(self.style.SUCCESS(f"Successfully scraped {source_name}"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to scrape {source_name}: {str(e)}")
            )
            logger.error(f"Failed to scrape {source_name}: {str(e)}")
            raise CommandError(f"Scraping failed: {str(e)}")
