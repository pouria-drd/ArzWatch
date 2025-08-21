import logging
from typing import List, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import InstrumentModel, SourceConfigModel
from ...sources import TgjuScraper, ZarminexScraper, WallexScraper

logger = logging.getLogger(__name__)

SCRAPER_MAP = {
    "tgju": TgjuScraper,
    "zarminex": ZarminexScraper,
    "wallex": WallexScraper,
}


class Command(BaseCommand):
    help = (
        "Scrape price data for a specific instrument. "
        "Prefers the instrument's default source; falls back to other enabled sources. "
        "Use --all-sources to scrape from all eligible sources."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "symbol",
            type=str,
            help="Instrument symbol to scrape (e.g., USD, EUR, BTC).",
        )
        parser.add_argument(
            "--all-sources",
            action="store_true",
            help="Scrape from ALL enabled sources for this instrument (not just the first success).",
        )
        parser.add_argument(
            "--auto-driver",
            action="store_true",
            help="Use webdriver_manager to auto-install ChromeDriver.",
        )

    def _resolve_sources(self, instrument: InstrumentModel):
        """Return a list of enabled sources, default first then others."""
        sources: List = []
        if instrument.default_source and instrument.default_source.enabled:
            sources.append(instrument.default_source)

        others = [
            cfg.source
            for cfg in SourceConfigModel.objects.filter(
                instrument=instrument, source__enabled=True
            ).exclude(source=instrument.default_source)
        ]
        sources.extend(others)
        return sources

    def handle(self, *args, **options):
        symbol = options["symbol"].upper()
        all_sources = options["all_sources"]
        auto_driver = options["auto_driver"]

        try:
            instrument = InstrumentModel.objects.get(symbol=symbol, enabled=True)
        except InstrumentModel.DoesNotExist:
            msg = f"Instrument '{symbol}' not found or disabled."
            logger.error(msg)
            raise CommandError(msg)

        sources = self._resolve_sources(instrument)
        if not sources:
            msg = f"No enabled sources found for instrument '{symbol}'."
            logger.warning(msg)
            raise CommandError(msg)

        successes: List[str] = []
        failures: List[Tuple[str, str]] = []

        for source in sources:
            scraper_cls = SCRAPER_MAP.get(source.name.lower())
            if not scraper_cls:
                warn = f"No scraper defined for source '{source.name}'."
                logger.warning(warn)
                self.stderr.write(self.style.WARNING(warn))
                continue

            try:
                self.stdout.write(
                    self.style.NOTICE(f"Scraping {symbol} from {source.name}...")
                )
                scraper = scraper_cls(
                    source, auto_driver=auto_driver, instruments=[symbol]
                )
                scraper.scrape()
                successes.append(source.name)
                self.stdout.write(
                    self.style.SUCCESS(f"OK: {symbol} from {source.name}")
                )
                logger.info(f"Successfully scraped {symbol} from {source.name}")

                if not all_sources:
                    break  # stop after first success unless --all-sources
            except Exception as e:
                failures.append((source.name, str(e)))
                self.stderr.write(
                    self.style.ERROR(f"FAIL: {symbol} from {source.name} → {e}")
                )
                logger.exception(f"Failed to scrape {symbol} from {source.name}: {e}")
                continue

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Successes: {successes or '—'}"))
        if failures:
            for name, err in failures:
                self.stderr.write(self.style.WARNING(f"Failed: {name} → {err}"))

        # Exit code
        if not successes:
            raise CommandError(f"All sources failed for {symbol}")
