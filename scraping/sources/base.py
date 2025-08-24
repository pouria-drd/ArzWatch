import os
import logging
import platform
from dotenv import load_dotenv


from typing import List, Dict, Any
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from django.conf import settings
from django.db import transaction
from ..models import InstrumentModel, PriceTickModel

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


SCRAPING_SLEEP_TIME = int(os.getenv("SCRAPING_SLEEP_TIME", 5))


class BaseScraper(ABC):
    def __init__(self, source, auto_driver=False):
        self.driver = None
        self.source = source
        self.auto_driver = auto_driver
        self.sleep_time = SCRAPING_SLEEP_TIME

    def init_driver(self):
        driver_path = (
            f"{settings.BASE_DIR}/scraping/sources/drivers/chromedriver.exe"
            if platform.system() == "Windows"
            else f"{settings.BASE_DIR}/scraping/sources/drivers/chromedriver"
        )
        service = (
            Service(driver_path)
            if not self.auto_driver
            else Service(ChromeDriverManager().install())
        )
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        self.driver = webdriver.Chrome(service=service, options=options)

    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        pass

    def scrape(self):
        if not self.source.enabled:
            logger.warning(f"Source {self.source.name} is disabled.")
            return

        self.init_driver()
        try:
            data = self.fetch_data() or []
            if not data:
                logger.info(f"No data fetched from {self.source.name}")
                return

            symbols = [d.get("symbol") for d in data if d.get("symbol")]
            inst_map = {
                i.symbol: i for i in InstrumentModel.objects.filter(symbol__in=symbols)
            }

            objs = []
            for d in data:
                inst = inst_map.get(d["symbol"])
                if not inst:
                    logger.warning(f"Instrument not found: {d['symbol']}")
                    continue
                objs.append(
                    PriceTickModel(
                        instrument=inst,
                        source=self.source,
                        price=d["price"],
                        currency=d.get("currency") or "IRR",
                        meta=d.get("meta") or {},
                    )
                )

            with transaction.atomic():
                PriceTickModel.objects.bulk_create(objs, ignore_conflicts=True)

            logger.info(f"Saved {len(objs)} ticks for {self.source.name}")

        except Exception as e:
            logger.exception(f"Failed to scrape {self.source.name}: {e}")
        finally:
            if self.driver:
                self.driver.quit()
