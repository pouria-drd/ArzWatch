import time
import logging
from typing import List, Dict, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from .base import BaseScraper
from ..models import SourceConfigModel
from ..utils import to_decimal, normalize_digits

logger = logging.getLogger(__name__)


class ArzDigitalScraper(BaseScraper):
    """
    Scraper to fetch cryptocurrency prices from https://arzdigital.com/.
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
            name = config.instrument.name
            path = config.path
            url = f"{self.source.base_url}/{path}"
            try:
                logger.info(f"Fetching data for {symbol} from {url}")
                self.driver.get(url)  # type: ignore

                # Wait for the price element to load
                WebDriverWait(self.driver, 30).until(  # type: ignore
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.arz-coin-page-data__coin-price")
                    )
                )

                # Wait for the page to load all data
                time.sleep(self.sleep_time)

                soup = BeautifulSoup(self.driver.page_source, "html.parser")  # type: ignore
                data: Dict[str, Any] = {
                    "symbol": symbol,
                    "currency": "USDT",  # Default to USDT
                    "meta": {"source_url": url},
                }

                # Extract USD price
                price_elem = soup.select_one("div.arz-coin-page-data__coin-price")
                if not price_elem:
                    raise ValueError("USD price not found")
                price_str = (
                    normalize_digits(price_elem.get_text(strip=True))
                    .replace("$", "")
                    .replace(",", "")
                )
                data["price"] = to_decimal(price_str)

                # Extract IRR price for meta
                irr_price_elem = soup.select_one(f"span.pulser-toman-{name.lower()}")
                if irr_price_elem:
                    irr_price = (
                        normalize_digits(irr_price_elem.get_text(strip=True))
                        .replace(" ت", "")
                        .replace(",", "")
                    )

                    data["meta"]["price_irr"] = str(
                        int(irr_price) * 10
                    )  # convert to rial

                # Extract price swing (changes)
                swing_elem = soup.select_one(
                    "div.arz-coin-page-data__coin-price-swing span"
                )
                if swing_elem:
                    data["meta"]["change_1h"] = normalize_digits(
                        swing_elem.get_text(strip=True)
                    )

                # Extract market info
                market_info = soup.select("div.arz-coin-page-data__coin-market-info")
                for info in market_info:
                    title = info.select_one(
                        "span.arz-coin-page-data__coin-market-info-title"
                    )
                    value = info.select_one(
                        "span.arz-coin-page-data__coin-market-info-value"
                    )
                    if title and value:
                        title_text = normalize_digits(title.get_text(strip=True))
                        value_text = normalize_digits(
                            value.get_text(strip=True)
                        ).replace(",", "")
                        if "معاملات روزانه" in title_text:
                            data["meta"]["daily_volume"] = value_text
                        elif "ارزش بازار" in title_text:
                            data["meta"]["market_cap"] = value_text
                        elif "سکه در گردش" in title_text:
                            data["meta"]["circulating_supply"] = value_text
                        elif "ارزش بازار رقیق شده" in title_text:
                            data["meta"]["fully_diluted_market_cap"] = value_text

                # Extract 24h high/low
                high_low = soup.select_one("div.arz-coin-page-data__coin-market-info")
                if high_low:
                    high_low_text = normalize_digits(high_low.get_text(strip=True))
                    if "بالاترین قیمت 24 ساعت اخیر" in high_low_text:
                        high_price = (
                            high_low_text.split(" / ")[0]
                            .replace("$", "")
                            .replace(",", "")
                        )
                        data["meta"]["highest_price_24h"] = high_price
                        low_price = (
                            high_low_text.split(" / ")[1]
                            .replace("$", "")
                            .replace(",", "")
                        )
                        data["meta"]["lowest_price_24h"] = low_price

                # Add IRR price as a separate entry
                # if "price_irr" in data["meta"]:
                #     irr_data = {
                #         "symbol": symbol,
                #         "currency": "IRR",
                #         "price": to_decimal(data["meta"]["price_irr"]),
                #         "meta": data["meta"].copy(),
                #     }
                #     results.append(irr_data)

                results.append(data)
                logger.debug(f"Extracted data for {symbol}: {data}")

            except TimeoutException as e:
                logger.error(f"Timeout waiting for page to load: {url}")
                raise
            except WebDriverException as e:
                logger.error(f"Selenium error fetching data from {url}: {str(e)}")
                raise
            except ValueError as e:
                logger.error(f"Parsing error for {symbol}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error fetching data from {url}: {str(e)}")
                continue

        return results
