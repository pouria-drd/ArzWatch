import json
from bs4 import BeautifulSoup
from .base_extractor import BaseExtractor
from typing import Dict, List, Optional, Union


class GoldExtractor(BaseExtractor):
    """
    Extracts gold data from the https://alanchand.com/gold-price website.
    """

    _gold_titles = {
        "مثقال طلا": "Gold Misqal",
        "یک گرم طلای 18 عیار": "18k Gold per Gram",
        "انس طلا": "Gold Ounce",
    }

    def extract_gold_data(
        self, soup: BeautifulSoup, format: Optional[str] = None
    ) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """
        Extracts gold data from the https://alanchand.com/gold-price website.

        Args:
            soup: The BeautifulSoup object.
            format: The format of the data to be returned. (json)
        """
        rows = soup.find_all("div", class_="col-lg-12")
        golds = []

        for row in rows:
            item = self._parse_item(row, self._gold_titles)
            if item:
                golds.append(item)

        last_update = self.extract_last_update(soup)

        result = {
            "last_update": last_update,
            "golds": golds,
        }

        if format == "json":
            return json.dumps(result, ensure_ascii=False, indent=4)

        return result

    def _parse_item(self, row, title_map) -> Optional[Dict[str, str]]:
        """
        Extracts a single item (gold/coin) from the row.
        """
        title_tag = row.find("div", class_="persian")
        if not title_tag:
            return None

        title = title_tag.text.strip()
        if title not in title_map:
            return None

        cells = row.find_all("div", class_="cell")
        price = cells[0].text.strip() if len(cells) > 0 else ""
        change = cells[1].text.strip() if len(cells) > 1 else ""
        bubble = cells[2].text.strip() if len(cells) > 2 else ""
        bubble_amount, bubble_percent = self._split_bubble(bubble)

        return {
            "title": title_map[title],
            "price": price,
            "change": change,
            "bubble_amount": bubble_amount,
            "bubble_percentage": bubble_percent,
        }

    def _split_bubble(self, bubble: str) -> tuple[str, str]:
        """
        Splits the bubble into amount and percentage.
        """
        if "%" in bubble:
            amount, percent = bubble.split("%")
            return amount.strip(), percent.strip() + "%"
        return "", ""
