import time
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .base import BaseScraper
from ..models import SourceConfigModel
from ..utils import to_decimal, normalize_digits

logger = logging.getLogger(__name__)


class MilliScraper(BaseScraper):
    """
    Scraper to fetch prices from https://milli.ir
    Uses SourceConfigModel for configurations.
    Returns a list of dicts: symbol, price, currency, meta
    """

    def __init__(
        self, source, auto_driver: bool = False, instruments: List[str] | None = None
    ):
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((TimeoutException, WebDriverException)),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying {retry_state.fn.__name__} (attempt {retry_state.attempt_number})..."  # type: ignore
        ),
    )
    def fetch_data(self) -> List[Dict[str, Any]]:
        if not self.source_configs.exists():
            return []

        results: List[Dict[str, Any]] = []

        for config in self.source_configs:
            symbol = config.instrument.symbol
            path = config.path
            url = f"{self.source.base_url}/{path}"
            try:
                logger.info(f"Fetching data for {symbol} from {url}")
                self.driver.get(url)  # type: ignore

                # Wait for the bx_coin div to load
                WebDriverWait(self.driver, 30).until(  # type: ignore
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.bx_coin"))
                )

                # Wait for the page to load all data
                time.sleep(self.sleep_time)

                soup = BeautifulSoup(self.driver.page_source, "html.parser")  # type: ignore
                bx_coin = soup.select_one("div.bx_coin")
                if not bx_coin:
                    raise ValueError("bx_coin div not found")

                data: Dict[str, Any] = {
                    "symbol": symbol,
                    "currency": "IRR",
                    "meta": {"source_url": url},
                }

                # Extract data from bx_coin div
                price_elem = bx_coin.select_one("div.last_price_coin span")
                if price_elem:
                    price_text = normalize_digits(
                        price_elem.get_text(strip=True)
                    ).replace(",", "")
                    data["price"] = to_decimal(price_text)
                    logger.debug(f"Extracted price for {symbol}: {price_text} IRR")
                else:
                    raise ValueError("Last price not found")

                change_percentage_elem = bx_coin.select_one("div.discount_coin span")
                if change_percentage_elem:
                    change_percentage = normalize_digits(
                        change_percentage_elem.get_text(strip=True)
                    )
                    data["meta"]["change_percentage"] = change_percentage
                    logger.debug(
                        f"Extracted change_percentage for {symbol}: {change_percentage}"
                    )
                else:
                    logger.warning(f"Change percentage not found for {symbol}")

                change_amount_elem = bx_coin.select_one("div.change_coin span")
                if change_amount_elem:
                    change_amount = normalize_digits(
                        change_amount_elem.get_text(strip=True)
                    ).replace(",", "")
                    data["meta"]["change_amount"] = change_amount
                    logger.debug(
                        f"Extracted change_amount for {symbol}: {change_amount}"
                    )
                else:
                    logger.warning(f"Change amount not found for {symbol}")

                bubble_elem = bx_coin.select_one("div.blubbe_coin span")
                if bubble_elem:
                    bubble = normalize_digits(bubble_elem.get_text(strip=True)).replace(
                        ",", ""
                    )
                    data["meta"]["bubble"] = bubble
                    logger.debug(f"Extracted bubble for {symbol}: {bubble}")
                else:
                    logger.warning(f"Bubble not found for {symbol}")

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
