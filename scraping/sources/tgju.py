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


class TgjuScraper(BaseScraper):
    """
    Scraper to fetch prices from tgju.org.
    Uses SourceConfigModel for configurations.
    Returns a list of dictionaries with symbol, price, currency, and metadata.
    """

    def __init__(self, source, auto_driver=False, instruments: List[str] = None):  # type: ignore
        super().__init__(source, auto_driver)
        # If instruments provided, filter instruments; otherwise, use all instruments for the source
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

                # Wait for the table to load (timeout after 10 seconds)
                WebDriverWait(self.driver, 10).until(  # type: ignore
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "tbody.table-padding-lg")
                    )
                )

                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, "html.parser")  # type: ignore
                table = soup.select_one("tbody.table-padding-lg")
                if not table:
                    raise ValueError("Price table not found")

                # Extract rows
                rows = table.find_all("tr")
                if not rows:
                    raise ValueError("No rows found in price table")

                # Initialize data dictionary
                data = {
                    "symbol": symbol,
                    "currency": "IRR",
                    "meta": {"source_url": url},
                }

                # Extract data from rows
                for row in rows:
                    cells = row.find_all("td")  # type: ignore
                    if len(cells) != 2:
                        continue
                    label = cells[0].text.strip()
                    value = cells[1].text.strip()

                    if label == "نرخ فعلی":  # Current price
                        price_str = value.replace(",", "")  # Remove commas
                        data["price"] = Decimal(price_str)
                    elif label == "بالاترین قیمت روز":  # Highest price
                        data["meta"]["highest_price"] = value.replace(",", "")
                    elif label == "پایین ترین قیمت روز":  # Lowest price
                        data["meta"]["lowest_price"] = value.replace(",", "")
                    elif label == "درصد تغییر نسبت به روز گذشته":  # Percentage change
                        data["meta"]["change_percentage"] = value
                    elif label == "زمان ثبت آخرین نرخ":  # Timestamp
                        data["meta"]["timestamp"] = value
                    elif label == "قیمت ریالی":
                        data["meta"]["rial_price"] = value.replace(",", "")

                if "price" not in data:
                    raise ValueError("Current price not found")

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
