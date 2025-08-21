import time
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


class WallexScraper(BaseScraper):
    """
    Scraper to fetch cryptocurrency prices from https://wallex.ir/.
    Uses SourceConfigModel for configurations.
    Returns a list of dictionaries with symbol, price (in USDT), currency, and metadata.
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

                # Wait for the main price (USDT) to load
                WebDriverWait(self.driver, 20).until(  # type: ignore
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.MuiTypography-BodyLargeMedium span")
                    )
                )

                # Stay on the page for 2 seconds before scraping
                time.sleep(2)

                # Parse page source
                soup = BeautifulSoup(self.driver.page_source, "html.parser")  # type: ignore

                # Initialize data dictionary
                data: Dict[str, Any] = {
                    "symbol": symbol,
                    "currency": "USDT",
                    "meta": {"source_url": url},
                }

                # Current price (USDT)
                price_elem = soup.select_one("div.MuiTypography-BodyLargeMedium span")
                if price_elem:
                    price_str = (
                        price_elem.text.replace("$", "").replace(",", "").strip()
                    )
                    data["price"] = Decimal(price_str)
                else:
                    raise ValueError("Current price (USDT) not found")

                # Percentage change (24h)
                perc_change_elem = soup.select_one("div.MuiStack-root span:last-child")
                if perc_change_elem and "%" in perc_change_elem.find_parent().text:  # type: ignore
                    data["meta"]["change_percentage"] = perc_change_elem.find_parent().text.strip()  # type: ignore

                # IRR price
                irr_price_elem = soup.select_one("div.MuiTypography-DisplayStrong span")
                if irr_price_elem:
                    irr_price_str = irr_price_elem.text.replace(",", "").strip()
                    data["meta"]["price_irr"] = irr_price_str

                # Highest price (24h, USDT)
                highest_price_elem = soup.select_one(
                    "div.MuiTypography-BodyMedium span", text=lambda x: x and "$" in x
                )
                if highest_price_elem:
                    data["meta"]["highest_price_usdt"] = (
                        highest_price_elem.text.replace("$", "")
                        .replace(",", "")
                        .strip()
                    )

                # Lowest price (24h, USDT)
                lowest_price_elems = soup.select("div.MuiTypography-BodyMedium span")
                for elem in lowest_price_elems:
                    if "$" in elem.text and elem != highest_price_elem:
                        data["meta"]["lowest_price_usdt"] = (
                            elem.text.replace("$", "").replace(",", "").strip()
                        )
                        break

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
