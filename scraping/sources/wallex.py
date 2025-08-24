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
from ..utils import to_decimal, normalize_digits, extract_first_number

logger = logging.getLogger(__name__)


class WallexScraper(BaseScraper):
    """
    Scraper to fetch cryptocurrency prices from https://wallex.ir/.
    Uses SourceConfigModel for configurations.
    Returns a list of dicts: symbol, price (USDT), currency, meta
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

                # Wait for the USDT price to render
                WebDriverWait(self.driver, 30).until(  # type: ignore
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "div.MuiTypography-BodyLargeMedium span")
                    )
                )

                # Wait for the page to load all data
                time.sleep(self.sleep_time)

                soup = BeautifulSoup(self.driver.page_source, "html.parser")  # type: ignore

                data: Dict[str, Any] = {
                    "symbol": symbol,
                    "currency": "USDT",
                    "meta": {"source_url": url},
                }

                # --- Current price (USDT) ---
                price_elem = soup.select_one("div.MuiTypography-BodyLargeMedium span")
                if not price_elem:
                    raise ValueError("Current price (USDT) not found")
                price_str = price_elem.get_text(strip=True).replace("$", "")
                data["price"] = to_decimal(price_str)

                # --- Percentage change (24h) ---
                change_value = None
                for node in soup.find_all(["div", "span"]):
                    txt = node.get_text(" ", strip=True)
                    if not txt:
                        continue
                    if "%" in normalize_digits(txt):
                        num = extract_first_number(txt)
                        if num is not None:
                            change_value = f"{num}%"
                            break
                if change_value:
                    data["meta"]["change_percentage"] = change_value

                # --- IRR price ---
                irr_price_elem = soup.select_one("div.MuiTypography-DisplayStrong span")
                if irr_price_elem:
                    irr_price_str = normalize_digits(
                        irr_price_elem.get_text(strip=True)
                    ).replace(",", "")
                    data["meta"]["price_irr"] = irr_price_str

                # --- Highest / Lowest price (24h, USDT) ---
                def extract_price_after_label(label_text: str) -> str | None:
                    for block in soup.find_all("div", class_=lambda c: c and "MuiStack-root" in c):  # type: ignore
                        block_text = block.get_text(" ", strip=True)
                        if label_text in block_text:
                            span = next(
                                (sp for sp in block.find_all("span") if "$" in sp.get_text()),  # type: ignore
                                None,
                            )
                            if span:
                                return span.get_text(strip=True)
                    return None

                highest_raw = extract_price_after_label("بیشترین قیمت")
                lowest_raw = extract_price_after_label("کمترین قیمت")

                if highest_raw:
                    data["meta"]["highest_price_usdt"] = normalize_digits(
                        highest_raw.replace("$", "").replace(",", "").strip()
                    )
                if lowest_raw:
                    data["meta"]["lowest_price_usdt"] = normalize_digits(
                        lowest_raw.replace("$", "").replace(",", "").strip()
                    )

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
