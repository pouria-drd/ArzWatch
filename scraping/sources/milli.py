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


class MilliScraper(BaseScraper):
    """
    Scraper to fetch Bahar coin data from https://milli.gold
    Uses SourceConfigModel for configurations.
    Returns a list of dicts: symbol, price, currency, meta
    """

    def __init__(self, source, auto_driver: bool = False, instruments: List[str] | None = None):  # type: ignore
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
            url = f"{self.source.base_url}/{config.path}"
            try:
                logger.info(f"Fetching data for {symbol} from {url}")
                self.driver.get(url)  # type: ignore

                # Wait for the container to load
                WebDriverWait(self.driver, 30).until(  # type: ignore
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.bx_coin"))
                )

                time.sleep(self.sleep_time)

                soup = BeautifulSoup(self.driver.page_source, "html.parser")  # type: ignore
                coin_div = soup.select_one("div.bx_coin")
                if not coin_div:
                    raise ValueError("Coin info container not found")

                data: Dict[str, Any] = {
                    "symbol": symbol,
                    "currency": "IRR",
                    "meta": {"source_url": url},
                }

                for item in coin_div.find_all("div"):
                    label = normalize_digits(item.find("label").get_text(strip=True))  # type: ignore
                    value = normalize_digits(item.find("span").get_text(strip=True))  # type: ignore

                    if "آخرین قیمت" in label:
                        data["price"] = to_decimal(value)
                    elif "درصد تغییر" in label:
                        data["meta"]["change_percentage"] = to_decimal(value)
                    elif "مقدار تغییر" in label:
                        data["meta"]["change_amount"] = to_decimal(value)
                    elif "حباب" in label:
                        data["meta"]["bubble"] = to_decimal(value)

                if "price" not in data:
                    raise ValueError("Current price not found")

                # Convert any Decimal in meta to float for JSONField
                for key, val in data["meta"].items():
                    if isinstance(val, Decimal):
                        data["meta"][key] = float(val)

                # Also convert price to float if needed
                if isinstance(data["price"], Decimal):
                    data["price"] = float(data["price"])

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
