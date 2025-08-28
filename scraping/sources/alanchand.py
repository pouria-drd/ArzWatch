import time
import logging
from decimal import Decimal
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


class AlanchandScraper(BaseScraper):
    """
    Scraper to fetch Bahar Azadi coin prices from https://alanchand.com
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
        logger.debug(f"Configs found: {self.source_configs.count()} for {source.name}")

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
            logger.error("No source configs found, returning empty results")
            return []

        results: List[Dict[str, Any]] = []

        for config in self.source_configs:
            symbol = config.instrument.symbol
            url = f"{self.source.base_url}/{config.path}"
            logger.info(f"Fetching data for {symbol} from {url}")

            try:
                self.driver.get(url)  # type: ignore
                logger.debug(f"Page loaded: {url}")

                WebDriverWait(self.driver, 30).until(  # type: ignore
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.goldPriceBox")
                    )
                )
                logger.debug("goldPriceBox div found")

                time.sleep(self.sleep_time)
                logger.debug(f"Waited {self.sleep_time} seconds for page to stabilize")

                soup = BeautifulSoup(self.driver.page_source, "html.parser")  # type: ignore
                gold_price_box = soup.select_one("div.goldPriceBox")
                if not gold_price_box:
                    logger.error("goldPriceBox div not found")
                    raise ValueError("goldPriceBox div not found")

                data: Dict[str, Any] = {
                    "symbol": symbol,
                    "currency": "IRR",
                    "meta": {"source_url": url},
                }

                # Extract last price
                price_elem = gold_price_box.select_one("span.fw-bold.text-success.fs-5")
                if price_elem:
                    price_text = normalize_digits(
                        price_elem.get_text(strip=True)
                    ).replace(",", "")
                    data["price"] = to_decimal(price_text)
                    logger.debug(f"Extracted price for {symbol}: {price_text} IRR")
                else:
                    logger.error("Last price not found")
                    raise ValueError("Last price not found")

                # Extract change percentage
                change_percentage_elem = gold_price_box.select_one(
                    "span.priceSymbol span.fs-7"
                )
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

                # Extract real price
                real_price_elem = gold_price_box.select_one(
                    "div.d-flex.justify-content-between:nth-child(1) > span:nth-child(2)"
                )
                if real_price_elem:
                    real_price = normalize_digits(
                        real_price_elem.get_text(strip=True)
                    ).replace(",", "")
                    data["meta"]["real_price"] = to_decimal(real_price)
                    logger.debug(f"Extracted real_price for {symbol}: {real_price}")
                else:
                    logger.warning(f"Real price not found for {symbol}")

                # Extract bubble and bubble percentage
                bubble_elem = gold_price_box.select_one(
                    "div.d-flex.justify-content-between:nth-child(2) > div > span:nth-child(2)"
                )
                bubble_percentage_elem = gold_price_box.select_one(
                    "div.d-flex.justify-content-between:nth-child(2) > div > span.ms-1"
                )
                if bubble_elem and bubble_percentage_elem:
                    bubble = normalize_digits(bubble_elem.get_text(strip=True)).replace(
                        ",", ""
                    )
                    bubble_percentage = normalize_digits(
                        bubble_percentage_elem.get_text(strip=True)
                    ).strip("()")
                    data["meta"]["bubble"] = to_decimal(bubble)
                    data["meta"]["bubble_percentage"] = bubble_percentage
                    logger.debug(f"Extracted bubble for {symbol}: {bubble}")
                    logger.debug(
                        f"Extracted bubble_percentage for {symbol}: {bubble_percentage}"
                    )
                else:
                    logger.warning(
                        f"Bubble or bubble percentage not found for {symbol}"
                    )

                # Convert Decimal in meta to float for JSONField
                for key, val in data["meta"].items():
                    if isinstance(val, Decimal):
                        data["meta"][key] = float(val)

                # Convert price to float if needed
                if isinstance(data["price"], Decimal):
                    data["price"] = float(data["price"])

                logger.debug(f"Final data for {symbol}: {data}")
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

        logger.info(f"Returning {len(results)} results from {self.source.name}")
        return results
