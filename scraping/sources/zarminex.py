import logging
from decimal import Decimal
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from .base import BaseScraper
from ..models import SourceConfigModel

logger = logging.getLogger(__name__)


class ZarminexScraper(BaseScraper):
    """
    Scraper to fetch gold prices from https://zarminex.ir/.
    Uses SourceConfigModel for configurations.
    Returns a list of dictionaries with symbol, price, currency, and metadata.
    """

    def __init__(self, source, auto_driver=False, instruments: List[str] = None):  # type: ignore
        super().__init__(source, auto_driver)
        self.source_configs = SourceConfigModel.objects.filter(source=source)
        if instruments:
            self.source_configs = self.source_configs.filter(
                instrument__symbol__in=instruments
            )
        if not self.source_configs.exists():
            logger.warning(
                f"No configurations found for source {source.name} for instruments {instruments}"
            )

    def fetch_data(self) -> List[Dict[str, Any]]:
        if not self.source_configs.exists():
            return []

        results = []
        for config in self.source_configs:
            symbol = config.instrument.symbol
            path = config.path
            url = f"{self.source.base_url}/{path}"

            try:
                logger.info(f"Fetching data for {symbol} from {url}")
                self.driver.get(url)  # type: ignore

                # Wait for the main gold price to load
                WebDriverWait(self.driver, 20).until(  # type: ignore
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[contains(text(),'ریال')]")
                    )
                )

                # Parse page source
                soup = BeautifulSoup(self.driver.page_source, "html.parser")  # type: ignore

                # Initialize data dictionary
                data: Dict[str, Any] = {
                    "symbol": symbol,
                    "currency": "IRR",
                    "meta": {"source_url": url},
                }

                # Current price
                price_elem = soup.find("span", text=lambda x: x and "ریال" in x)  # type: ignore
                if price_elem:
                    price_str = (
                        price_elem.text.replace(",", "").replace("ریال", "").strip()
                    )
                    data["price"] = Decimal(price_str)

                # Last update date
                last_update_elem = soup.find("span", text=lambda x: x and "/" in x)  # type: ignore
                if last_update_elem:
                    data["meta"]["last_update"] = last_update_elem.text.strip()

                # Percentage change
                perc_change_elem = soup.find("span", text=lambda x: x and "%" in x)  # type: ignore
                if perc_change_elem:
                    data["meta"]["change_percentage"] = perc_change_elem.text.strip()

                # Amount change
                amount_change_elem = perc_change_elem.find_parent("div").find_next_sibling("div")  # type: ignore
                if amount_change_elem:
                    data["meta"][
                        "change_amount"
                    ] = amount_change_elem.text.strip().replace(",", "")

                results.append(data)

            except TimeoutException:
                logger.error(f"Timeout waiting for page to load: {url}")
                continue
            except WebDriverException as e:
                logger.error(f"Selenium error fetching data from {url}: {str(e)}")
                continue
            except ValueError as e:
                logger.error(f"Parsing error for {symbol}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error fetching data from {url}: {str(e)}")
                continue

        return results
