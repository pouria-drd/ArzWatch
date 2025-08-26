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


class WallexScraper(BaseScraper):
    """
    Scraper to fetch cryptocurrency details from https://wallex.ir/.
    Parses the detail table (name, price, change %, market cap, supply, etc.)
    """

    def __init__(self, source, auto_driver: bool = False, instruments: List[str] | None = None):  # type: ignore
        super().__init__(source, auto_driver)
        self.source_configs = SourceConfigModel.objects.filter(source=source)
        if instruments:
            self.source_configs = self.source_configs.filter(
                instrument__symbol__in=instruments
            )
        if not self.source_configs.exists():
            logger.warning(f"No configurations found for source {source.name}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((TimeoutException, WebDriverException)),
        before_sleep=lambda s: logger.warning(
            f"Retrying {s.fn.__name__} (attempt {s.attempt_number})..."  # type: ignore
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

                # Wait for the table to render
                WebDriverWait(self.driver, 30).until(  # type: ignore
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "table.MuiBox-root tbody tr")
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

                # --- Parse table rows ---
                rows = soup.select("table.MuiBox-root tbody tr")
                for row in rows:
                    th = row.find("th")
                    td = row.find("td")
                    if not th or not td:
                        continue

                    label = th.get_text(strip=True)
                    value = td.get_text(" ", strip=True)
                    value = normalize_digits(value)

                    # Map Persian label → meta keys
                    # extract name_fa
                    if "نام رمز‌ارز" in label:
                        data["meta"]["name_fa"] = value
                    # extract change_24h
                    elif "تغییرات ۲۴ ساعته" in label:
                        data["meta"]["change_24h"] = value
                    # extract price (USDT)
                    elif "قیمت دلاری" in label:
                        data["price"] = to_decimal(
                            value.replace("$", "").replace(",", "")
                        )
                    # extract price_irr (IRR)
                    elif "قیمت تومانی" in label:
                        data["meta"]["price_irr"] = str(
                            int(value.replace("تومان", "").replace(",", "").strip())
                            * 10
                        )
                    # extract volume_24h (USDT)
                    elif "حجم معاملات" in label:
                        data["meta"]["volume_24h"] = value
                    # extract market_cap (USDT)
                    elif "حجم کل بازار" in label:
                        data["meta"]["market_cap"] = value
                    # extract available_supply (USDT)
                    elif "ارز در دسترس" in label:
                        data["meta"]["available_supply"] = value
                    # extract max_supply (USDT)
                    elif "حداکثر قابل عرضه" in label:
                        data["meta"]["max_supply"] = value
                    # extract circulating_supply (USDT)
                    elif "ارز در گردش" in label:
                        data["meta"]["circulating_supply"] = value
                    # extract rank
                    elif "رتبه در بازار" in label:
                        data["meta"]["rank"] = value

                results.append(data)

            except Exception as e:
                logger.error(f"Error fetching {symbol} from {url}: {str(e)}")
                continue

        return results
