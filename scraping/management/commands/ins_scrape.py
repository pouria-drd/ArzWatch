import logging
from ...models import InstrumentModel, SourceConfigModel
from django.core.management.base import BaseCommand, CommandError
from ...sources import TgjuScraper, ZarminexScraper, WallexScraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrape price data for a specific instrument using its default source or fallback sources."

    def add_arguments(self, parser):
        parser.add_argument(
            "symbol", type=str, help="Instrument symbol to scrape (e.g., USD, EUR)"
        )

    def handle(self, *args, **options):
        symbol = options["symbol"].upper()
        try:
            instrument = InstrumentModel.objects.get(symbol=symbol, enabled=True)
        except InstrumentModel.DoesNotExist:
            logger.error(f"Instrument '{symbol}' not found or disabled")
            raise CommandError(f"Instrument '{symbol}' not found or disabled")

        # Try default source first
        sources = []
        if instrument.default_source and instrument.default_source.enabled:
            sources.append(instrument.default_source)
        # Add other sources from SourceConfigModel
        sources.extend(
            [
                config.source
                for config in SourceConfigModel.objects.filter(
                    instrument=instrument, source__enabled=True
                ).exclude(source=instrument.default_source)
            ]
        )

        if not sources:
            logger.warning(f"No enabled sources found for instrument '{symbol}'")
            raise CommandError(f"No enabled sources found for instrument '{symbol}'")

        scraper_class_map = {
            "tgju": TgjuScraper,
            "zarminex": ZarminexScraper,
            "wallex": WallexScraper,
        }

        for source in sources:
            scraper_class = scraper_class_map.get(source.name.lower())
            if not scraper_class:
                logger.warning(f"No scraper defined for source '{source.name}'")
                self.stderr.write(
                    self.style.WARNING(f"No scraper defined for source '{source.name}'")
                )
                continue

            try:
                logger.info(f"Scraping {symbol} from {source.name}")
                self.stdout.write(
                    self.style.SUCCESS(f"Scraping {symbol} from {source.name}...")
                )
                scraper = scraper_class(source, auto_driver=False, instruments=[symbol])
                scraper.scrape()
                logger.info(f"Successfully scraped {symbol} from {source.name}")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully scraped {symbol} from {source.name}"
                    )
                )
                return
            except Exception as e:
                logger.error(f"Failed to scrape {symbol} from {source.name}: {str(e)}")
                self.stderr.write(
                    f"Failed to scrape {symbol} from {source.name}: {str(e)}"
                )
                continue

        logger.error(f"All sources failed for {symbol}")
        self.stderr.write(self.style.ERROR(f"All sources failed for {symbol}"))
