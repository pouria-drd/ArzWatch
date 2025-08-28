"""
===============================================================================
ArzWatch Scrape Command (Django Management Command)
===============================================================================

Purpose
-------
Unified CLI entrypoint to run scrapers in different scopes with *default-first*
logic for instruments.

Core Rules
----------
1) Default-first per instrument:
   - If an instrument has an ACTIVE default source -> scrape ONLY that source.
   - Otherwise, fallback to the FIRST active configured source (via SourceConfigModel).
   - If none exists -> WARN and SKIP that instrument.

2) Source scoping:
   --source              : Run across ALL enabled sources (no restriction).
   --source <name>       : Run only the specified source (e.g., tgju).

3) Instrument scoping:
   --instrument          : Run across ALL enabled instruments.
   --instrument <symbol> : Run only the specified instrument (e.g., USD).

4) Mixing scopes:
   - If BOTH --instrument and --source are provided:
       Instrument scope is primary; the source option *narrows* behavior:
         * --instrument usd --source tgju  -> scrape USD from TGJU only.
         * --instrument usd --source       -> scrape USD from ALL its active sources.
   - If ONLY --instrument is provided:
       Default-first single-source logic applies (see Rule 1).
   - If ONLY --source is provided:
       Source-scoped run (iterate instruments configured for that source).

5) Driver:
   --auto-driver  : Use webdriver_manager to auto-install ChromeDriver.

Examples
--------
# Scrape ALL sources (each for its configured instruments)
python manage.py scrape --source

# Scrape ALL instruments (each picks default-first; fallback if needed)
python manage.py scrape --instrument

# Only TGJU (for its configured instruments)
python manage.py scrape --source tgju

# Only USD (default-first, otherwise fallback)
python manage.py scrape --instrument usd

# USD from a specific source
python manage.py scrape --instrument usd --source tgju

# USD from ALL its active sources (explicit)
python manage.py scrape --instrument usd --source

Notes
-----
- Extend SCRAPER_MAP when adding a new source.
- This command intentionally runs scrapers *sequentially* to avoid Selenium
  contention and rate-limits. Parallelization can be added later if needed.
===============================================================================
"""

import logging
from typing import List, Optional, Tuple

from django.core.management.base import BaseCommand, CommandError

from ...models import InstrumentModel, SourceModel, SourceConfigModel
from ...sources import (
    TgjuScraper,
    MilliScraper,
    WallexScraper,
    ZarminexScraper,
    AlanchandScraper,
    ArzDigitalScraper,
)

logger = logging.getLogger(__name__)

# Map source keys to scraper classes (extend here when adding new sources)
SCRAPER_MAP = {
    "tgju": TgjuScraper,
    "milli": MilliScraper,
    "wallex": WallexScraper,
    "zarminex": ZarminexScraper,
    "alanchand": AlanchandScraper,
    "arzdigital": ArzDigitalScraper,
}


class Command(BaseCommand):
    """
    Unified scraping command with flexible scopes.

    Core rules:
      - Default-first for instruments:
          If an instrument has an active default source -> scrape ONLY that.
          Otherwise, fallback to the first active configured source (via SourceConfigModel).
          If none exists -> warn and skip.

      - Source scoping:
          --source              : all enabled sources (no restriction)
          --source <name>       : only the specified source (e.g., tgju)

      - Instrument scoping:
          --instrument          : all enabled instruments
          --instrument <symbol> : only the specified instrument (e.g., USD)

    Supported combos:
      # scrape all sources (for their configured instruments)
      python manage.py scrape --source

      # scrape all instruments (each uses default-first, otherwise fallback)
      python manage.py scrape --instrument

      # only tgju (for its configured instruments)
      python manage.py scrape --source tgju

      # scrape just USD (default-first, otherwise fallback)
      python manage.py scrape --instrument usd

      # scrape USD but force a specific source
      python manage.py scrape --instrument usd --source tgju
      # (or use --source with no name to hit all active sources for USD)

    Notes:
      - You can combine --instrument and --source. Source scope narrows the run.
      - When --source is present, "default-first single-source" rule is bypassed
        because you explicitly asked for source-driven execution.
    """

    help = "Scrape market data with default-first behavior and optional source/instrument scoping."

    def add_arguments(self, parser):
        # Optional-argument flags with optional values:
        #   --source [NAME]      (NAME omitted => all sources)
        #   --instrument [SYMBOL] (SYMBOL omitted => all instruments)
        parser.add_argument(
            "--source",
            nargs="?",
            const="__ALL__",  # flag present, no value: all sources
            default=None,  # flag absent
            help="Specify a source key (e.g., tgju). If omitted value, run across ALL enabled sources.",
        )
        parser.add_argument(
            "--instrument",
            nargs="?",
            const="__ALL__",  # flag present, no value: all instruments
            default=None,  # flag absent
            help="Specify an instrument symbol (e.g., USD). If omitted value, run across ALL enabled instruments.",
        )
        parser.add_argument(
            "--auto-driver",
            action="store_true",
            help="Auto-install ChromeDriver via webdriver_manager (useful in ephemeral environments).",
        )

    # -------------------- helpers --------------------

    def _scraper_for(self, source_name: str):
        """Return scraper class by source name (case-insensitive), or None if unsupported."""
        return SCRAPER_MAP.get(source_name.lower())

    def _get_enabled_sources(self) -> List[SourceModel]:
        """All enabled sources."""
        return list(SourceModel.objects.filter(enabled=True))

    def _get_enabled_instruments(self) -> List[InstrumentModel]:
        """All enabled instruments."""
        return list(InstrumentModel.objects.filter(enabled=True))

    def _configured_symbols_for_source(self, source: SourceModel) -> List[str]:
        """Unique instrument symbols configured for a given source."""
        qs = SourceConfigModel.objects.filter(source=source).select_related(
            "instrument"
        )
        return sorted({cfg.instrument.symbol for cfg in qs})

    def _active_sources_for_instrument(
        self, instrument: InstrumentModel
    ) -> List[SourceModel]:
        """
        All active (enabled) sources configured for a given instrument (order preserved by DB).
        """
        cfgs = SourceConfigModel.objects.filter(
            instrument=instrument, source__enabled=True
        ).select_related("source")
        return [cfg.source for cfg in cfgs]

    def _default_first_single_source(
        self, instrument: InstrumentModel
    ) -> Optional[SourceModel]:
        """
        Enforce the default-first rule for a single instrument:
          - If default_source exists and is enabled -> return it.
          - Else return the first active configured source as fallback.
          - If none -> return None (caller should warn+skip).
        """
        if instrument.default_source and instrument.default_source.enabled:
            return instrument.default_source

        for src in self._active_sources_for_instrument(instrument):
            return src  # first active configured source (fallback)
        return None

    # -------------------- runners --------------------

    def _run_source_scope(
        self,
        source_key: Optional[str],
        auto_driver: bool,
        instruments_subset: Optional[List[str]] = None,
    ):
        """
        Source-scoped execution.

        - source_key == '__ALL__'  -> iterate over all enabled sources.
        - source_key == '<name>'   -> run only that source.
        - instruments_subset       -> if provided, limit instruments to this subset of symbols;
                                     otherwise, use the source's configured instruments.
        """
        sources: List[SourceModel]
        if source_key == "__ALL__":
            sources = self._get_enabled_sources()
        else:
            if not source_key:
                raise CommandError(
                    "Internal: _run_source_scope requires a source scope."
                )
            try:
                src = SourceModel.objects.get(name__iexact=source_key, enabled=True)
            except SourceModel.DoesNotExist:
                raise CommandError(f"Source '{source_key}' not found or disabled.")
            sources = [src]

        any_success = False
        failures: List[Tuple[str, str]] = []

        for source in sources:
            scraper_cls = self._scraper_for(source.name)
            if not scraper_cls:
                warn = f"No scraper defined for source '{source.name}'"
                self.stderr.write(self.style.WARNING(warn))
                logger.warning(warn)
                continue

            # Resolve instruments for this source
            if instruments_subset:
                symbols = instruments_subset
                # optionally ensure that each symbol is actually configured for this source
                configured = set(self._configured_symbols_for_source(source))
                symbols = [s for s in symbols if s in configured]
                if not symbols:
                    self.stderr.write(
                        self.style.WARNING(
                            f"[{source.name}] no matching configured instruments in the provided subset."
                        )
                    )
                    continue
            else:
                symbols = self._configured_symbols_for_source(source)
                if not symbols:
                    self.stderr.write(
                        self.style.WARNING(f"[{source.name}] no configured instruments")
                    )
                    continue

            self.stdout.write(
                self.style.NOTICE(
                    f"[{source.name}] scraping {len(symbols)} instrument(s)..."
                )
            )

            try:
                scraper = scraper_cls(
                    source, auto_driver=auto_driver, instruments=symbols
                )
                scraper.scrape()
                any_success = True
                self.stdout.write(self.style.SUCCESS(f"[{source.name}] DONE"))
            except Exception as e:
                failures.append((source.name, str(e)))
                self.stderr.write(self.style.ERROR(f"[{source.name}] FAIL → {e}"))
                logger.exception("Source-scoped error", exc_info=e)

        if not any_success and failures:
            # Report a single aggregated error for CI/ops visibility
            raise CommandError("Source scope failed for all targets.")

    def _run_instrument_scope(
        self,
        instrument_symbol: Optional[str],
        auto_driver: bool,
        source_key: Optional[str],
    ):
        """
        Instrument-scoped execution.

        Behavior matrix:
          - source_key is None:
              For each instrument -> pick exactly ONE source using default-first,
              else first active fallback; if none -> warn+skip.

          - source_key == '__ALL__':
              For each instrument -> scrape across ALL its active configured sources.

          - source_key == '<name>':
              For each instrument -> if that source is active & configured for it -> scrape it;
                                     otherwise warn+skip.
        """
        # Resolve instruments (single symbol or all)
        if instrument_symbol and instrument_symbol != "__ALL__":
            instruments = list(
                InstrumentModel.objects.filter(
                    symbol=instrument_symbol.upper(), enabled=True
                )
            )
            if not instruments:
                raise CommandError(
                    f"Instrument '{instrument_symbol}' not found or disabled."
                )
        else:
            instruments = self._get_enabled_instruments()
            if not instruments:
                raise CommandError("No enabled instruments found.")

        any_success = False
        failures: List[Tuple[str, str]] = []

        for inst in instruments:
            # Determine source set according to source_key mode
            sources: List[SourceModel] = []

            if source_key is None:
                # Default-first single source (or single fallback)
                picked = self._default_first_single_source(inst)
                if picked is None:
                    warn = f"[{inst.symbol}] no active default or fallback source; skipping."
                    self.stderr.write(self.style.WARNING(warn))
                    logger.warning(warn)
                    continue
                sources = [picked]

            elif source_key == "__ALL__":
                # All active configured sources for this instrument
                sources = self._active_sources_for_instrument(inst)
                if not sources:
                    warn = f"[{inst.symbol}] no active configured sources; skipping."
                    self.stderr.write(self.style.WARNING(warn))
                    logger.warning(warn)
                    continue

            else:
                # Specific source only
                try:
                    src = SourceModel.objects.get(name__iexact=source_key, enabled=True)
                except SourceModel.DoesNotExist:
                    warn = f"Source '{source_key}' not found/disabled; skipping {inst.symbol}."
                    self.stderr.write(self.style.WARNING(warn))
                    logger.warning(warn)
                    continue

                # Verify this instrument is configured for that source
                configured = SourceConfigModel.objects.filter(
                    source=src, instrument=inst
                ).exists()
                if not configured:
                    warn = f"[{inst.symbol}] not configured for source '{src.name}'; skipping."
                    self.stderr.write(self.style.WARNING(warn))
                    logger.warning(warn)
                    continue
                sources = [src]

            # Execute scraping for decided sources
            for src in sources:
                scraper_cls = self._scraper_for(src.name)
                if not scraper_cls:
                    warn = f"No scraper defined for source '{src.name}'"
                    self.stderr.write(self.style.WARNING(warn))
                    logger.warning(warn)
                    continue

                try:
                    self.stdout.write(
                        self.style.NOTICE(f"[{inst.symbol}] {src.name}: scraping...")
                    )
                    scraper = scraper_cls(
                        src, auto_driver=auto_driver, instruments=[inst.symbol]
                    )
                    scraper.scrape()
                    any_success = True
                    self.stdout.write(
                        self.style.SUCCESS(f"[{inst.symbol}] {src.name}: OK")
                    )
                except Exception as e:
                    failures.append((f"{inst.symbol}@{src.name}", str(e)))
                    self.stderr.write(
                        self.style.ERROR(f"[{inst.symbol}] {src.name}: FAIL → {e}")
                    )
                    logger.exception("Instrument-scoped error", exc_info=e)

        if not any_success and failures:
            raise CommandError("Instrument scope failed for all targets.")

    # -------------------- entrypoint --------------------

    def handle(self, *args, **options):
        """
        Entrypoint routing according to presence/value of --source and --instrument.
        Rules:
          - If only --source is provided  : run source-scoped execution.
          - If only --instrument is provided: run instrument-scoped execution (default-first logic).
          - If both are provided         : instrument scope takes precedence,
                                           with source_key narrowing its behavior.
        """
        auto_driver = options["auto_driver"]

        src_opt: Optional[str] = options.get("source")  # None | '__ALL__' | '<name>'
        inst_opt: Optional[str] = options.get(
            "instrument"
        )  # None | '__ALL__' | '<symbol>'

        # Validate at least one scope flag is present
        if src_opt is None and inst_opt is None:
            raise CommandError(
                "Usage: provide --source [NAME] or --instrument [SYMBOL] (or both)."
            )

        # Both provided -> instrument scope narrowed by source_key
        if inst_opt is not None and src_opt is not None:
            return self._run_instrument_scope(
                instrument_symbol=inst_opt,
                auto_driver=auto_driver,
                source_key=src_opt,
            )

        # Only source
        if src_opt is not None:
            return self._run_source_scope(
                source_key=src_opt,
                auto_driver=auto_driver,
                instruments_subset=None,  # no subset filter
            )

        # Only instrument
        return self._run_instrument_scope(
            instrument_symbol=inst_opt,
            auto_driver=auto_driver,
            source_key=None,  # triggers default-first single-source behavior
        )
