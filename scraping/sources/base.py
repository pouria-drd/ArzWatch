import logging
import platform
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


class BaseScraper(ABC):
    def __init__(self, source, auto_driver=False):
        self.driver = None
        self.source = source
        self.auto_driver = auto_driver

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
            data = self.fetch_data()
            with transaction.atomic():
                PriceTickModel.objects.bulk_create(
                    [
                        PriceTickModel(
                            instrument=InstrumentModel.objects.get(symbol=d["symbol"]),
                            source=self.source,
                            price=d["price"],
                            currency=d["currency"],
                            meta=d.get("meta"),
                        )
                        for d in data
                    ]
                )

                symbols = [d["symbol"] for d in data]
                logger.info(f"Saved ticks for {symbols} from {self.source.name}")

        except Exception as e:
            logger.exception(f"Failed to scrape {self.source.name}: {e}")
        finally:
            if self.driver:
                self.driver.quit()

    async def __aexit__(self, exc_type, exc, tb):
        if self.driver:
            self.driver.quit()
