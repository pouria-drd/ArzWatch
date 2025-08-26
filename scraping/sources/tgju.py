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


class TgjuScraper(BaseScraper):
    """
    Scraper to fetch prices from https://tgju.org
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
            path = config.path
            url = f"{self.source.base_url}/{path}"
            try:
                logger.info(f"Fetching data for {symbol} from {url}")
                self.driver.get(url)  # type: ignore

                # Wait for the table to load
                WebDriverWait(self.driver, 30).until(  # type: ignore
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "tbody.table-padding-lg")
                    )
                )

                # Wait for the page to load all data
                time.sleep(self.sleep_time)

                soup = BeautifulSoup(self.driver.page_source, "html.parser")  # type: ignore
                table = soup.select_one("tbody.table-padding-lg")
                if not table:
                    raise ValueError("Price table not found")

                rows = table.find_all("tr")
                if not rows:
                    raise ValueError("No rows found in price table")

                data: Dict[str, Any] = {
                    "symbol": symbol,
                    "currency": (
                        "USDT" if config.instrument.category == "crypto" else "IRR"
                    ),
                    "meta": {"source_url": url},
                }

                for row in rows:
                    cells = row.find_all("td")  # type: ignore
                    if len(cells) != 2:
                        continue
                    label = normalize_digits(cells[0].get_text(strip=True))
                    value = cells[1].get_text(strip=True)

                    if "نرخ فعلی" in label:
                        data["price"] = to_decimal(value)
                    elif "بالاترین قیمت روز" in label:
                        data["meta"]["highest_price"] = normalize_digits(value).replace(
                            ",", ""
                        )
                    elif "پایین ترین قیمت روز" in label:
                        data["meta"]["lowest_price"] = normalize_digits(value).replace(
                            ",", ""
                        )
                    elif "درصد تغییر" in label:
                        data["meta"]["change_percentage"] = normalize_digits(value)
                    elif "زمان ثبت آخرین نرخ" in label:
                        data["meta"]["timestamp"] = normalize_digits(value)
                    elif "قیمت ریالی" in label:
                        data["meta"]["price_irr"] = normalize_digits(value).replace(
                            ",", ""
                        )

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
