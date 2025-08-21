import re
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


def _normalize_digits(s: str) -> str:
    """Convert Persian/Arabic digits to ASCII digits."""
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٪", "01234567890123456789%")
    return s.translate(trans)


def _to_decimal(s: str) -> Decimal:
    s = _normalize_digits(s)
    s = re.sub(r"[^\d\.\-]", "", s)  # keep digits, dot, minus
    return Decimal(s)


class WallexScraper(BaseScraper):
    """
    Scraper to fetch cryptocurrency prices from https://wallex.ir/.
    Uses SourceConfigModel for configurations.
    Returns a list of dictionaries with symbol, price (in USDT), currency, and meta.
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

        results: List[Dict[str, Any]] = []

        for config in self.source_configs:
            symbol = config.instrument.symbol
            path = config.path
            url = f"{self.source.base_url}/{path}"

            try:
                logger.info(f"Fetching data for {symbol} from {url}")
                self.driver.get(url)  # type: ignore

                # Wait for the USDT price to render
                WebDriverWait(self.driver, 20).until(  # type: ignore
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "div.MuiTypography-BodyLargeMedium span")
                    )
                )

                # Small buffer to let other widgets hydrate
                time.sleep(2)

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
                price_str = price_elem.get_text(strip=True)
                data["price"] = _to_decimal(price_str)

                # --- Percentage change (24h) ---
                # Look for any node that contains either '%' or '٪', then extract the first number and normalize to ASCII '%'
                change_value = None
                for node in soup.find_all(["div", "span"]):
                    txt = node.get_text(" ", strip=True)
                    if not txt:
                        continue
                    if ("%" in txt) or ("٪" in txt):
                        m = re.search(r"([+-]?\d+(?:\.\d+)?)", _normalize_digits(txt))
                        if m:
                            change_value = f"{m.group(1)}%"
                            break
                if change_value:
                    data["meta"]["change_percentage"] = change_value

                # --- IRR price ---
                irr_price_elem = soup.select_one("div.MuiTypography-DisplayStrong span")
                if irr_price_elem:
                    irr_price_str = _normalize_digits(
                        irr_price_elem.get_text(strip=True)
                    ).replace(",", "")
                    data["meta"]["price_irr"] = irr_price_str

                # --- Highest / Lowest price (24h, USDT) ---
                # Find blocks that contain 'بیشترین قیمت' and 'کمترین قیمت' and then read the first '$' span inside them.
                def extract_price_after_label(label_text: str) -> str | None:
                    for block in soup.find_all(
                        "div", class_=lambda c: c and "MuiStack-root" in c  # type: ignore
                    ):
                        block_text = block.get_text(" ", strip=True)
                        if label_text in block_text:
                            # grab the first span in this block that contains a USD value
                            span = next(
                                (
                                    sp
                                    for sp in block.find_all("span")  # type: ignore
                                    if "$" in sp.get_text()
                                ),
                                None,
                            )
                            if span:
                                return span.get_text(strip=True)
                    return None

                highest_raw = extract_price_after_label("بیشترین قیمت")
                lowest_raw = extract_price_after_label("کمترین قیمت")

                if highest_raw:
                    data["meta"]["highest_price_usdt"] = _normalize_digits(
                        highest_raw.replace("$", "").replace(",", "").strip()
                    )
                if lowest_raw:
                    data["meta"]["lowest_price_usdt"] = _normalize_digits(
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
