import logging
from typing import List

from django.core.management.base import BaseCommand, CommandError

from ...models import SourceModel, SourceConfigModel, InstrumentModel
from ...sources import TgjuScraper, ZarminexScraper, WallexScraper

logger = logging.getLogger(__name__)

SCRAPER_MAP = {
    "tgju": TgjuScraper,
    "zarminex": ZarminexScraper,
    "wallex": WallexScraper,
}


class Command(BaseCommand):
    help = (
        "Scrape price data from a source for given instruments, or all configured instruments "
        "of that source if none are provided.\n"
        "Example: python manage.py scrape_source tgju USD EUR --category currency"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "source", type=str, help="Source key (e.g., tgju, wallex, zarminex)."
        )
        parser.add_argument(
            "instruments",
            nargs="*",
            type=str,
            help="Optional list of instrument symbols (e.g., USD EUR BTC). If omitted, scrape all configured.",
        )
        parser.add_argument(
            "--category",
            choices=[c for c, _ in InstrumentModel.Category.choices],
            help="Optional category filter when inferring instruments (gold/coin/currency/crypto).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Optional limit for number of instruments to scrape (useful for testing).",
        )
        parser.add_argument(
            "--auto-driver",
            action="store_true",
            help="Use webdriver_manager to auto-install ChromeDriver.",
        )

    def _infer_instruments(
        self, source: SourceModel, category: str | None
    ) -> List[str]:
        qs = SourceConfigModel.objects.filter(source=source).select_related(
            "instrument"
        )
        if category:
            qs = qs.filter(instrument__category=category)

        symbols = [cfg.instrument.symbol for cfg in qs]
        return sorted(set(symbols))

    def handle(self, *args, **options):
        source_key = options["source"].lower()
        auto_driver = options["auto_driver"]
        requested_instruments = [i.upper() for i in options["instruments"]]
        category = options.get("category")
        limit = options.get("limit") or 0

        scraper_cls = SCRAPER_MAP.get(source_key)
        if not scraper_cls:
            supported = ", ".join(SCRAPER_MAP.keys())
            msg = (
                f"No scraper defined for source '{source_key}'. Supported: {supported}"
            )
            logger.warning(msg)
            raise CommandError(msg)

        try:
            source = SourceModel.objects.get(name__iexact=source_key, enabled=True)
        except SourceModel.DoesNotExist:
            msg = f"Source '{source_key}' not found or disabled."
            logger.warning(msg)
            raise CommandError(msg)

        # Resolve instruments
        if requested_instruments:
            # validate requested
            exists = set(
                InstrumentModel.objects.filter(
                    symbol__in=requested_instruments, enabled=True
                ).values_list("symbol", flat=True)
            )
            missing = [s for s in requested_instruments if s not in exists]
            if missing:
                raise CommandError(
                    f"Unknown/disabled instruments: {', '.join(missing)}"
                )

            symbols = requested_instruments
        else:
            # infer from SourceConfig
            symbols = self._infer_instruments(source, category)
            if not symbols:
                raise CommandError(
                    f"No instruments configured for source '{source.name}'"
                    + (f" with category '{category}'." if category else ".")
                )

        if limit > 0:
            symbols = symbols[:limit]

        self.stdout.write(
            self.style.NOTICE(
                f"Scraping source '{source.name}' "
                f"for instruments: {symbols if len(symbols) <= 10 else (symbols[:10] + ['...'])}"
            )
        )

        try:
            scraper = scraper_cls(source, auto_driver=auto_driver, instruments=symbols)
            scraper.scrape()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully scraped '{source.name}'")
            )
            logger.info(
                f"Successfully scraped '{source.name}' for {len(symbols)} instruments."
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to scrape '{source.name}': {e}")
            )
            logger.exception(f"Failed to scrape '{source.name}': {e}")
            raise CommandError(f"Scraping failed: {e}")
