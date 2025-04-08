import json
from bs4 import BeautifulSoup
from .base import BaseExtractor
from typing import Dict, Optional


class CoinExtractor(BaseExtractor):
    """
    Extracts coin data from the https://alanchand.com/gold-price website.
    """

    _coin_titles = {
        "سکه امامی": "Imami Coin",
        "سکه بهار آزادی": "Bahare Azadi Coin",
        "نیم سکه": "Half Coin",
        "ربع سکه": "Quarter Coin",
        "سکه گرمی": "Gram Coin",
    }

    def extract_coin_data(
        self, soup: BeautifulSoup, format: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extracts coin data from the https://alanchand.com/gold-price website.

        Args:
            soup: The BeautifulSoup object.
            format: The format of the data to be returned. (json)
        """
        # Find all divs with class "col-lg-12"
        rows = soup.find_all("div", class_="col-lg-12")
        coins = []

        for row in rows:
            # Find the div with class "persian"
            title_tag = row.find("div", class_="persian")
            # Check if the title tag exists
            if not title_tag:
                continue

            # Get the text of the title tag
            title = title_tag.text.strip()
            # Check if the title is in the coin titles
            if title not in self._coin_titles:
                continue

            # Find all divs with class "cell"
            cells = row.find_all("div", class_="cell")
            # Get the text of the first cell
            price = cells[0].text.strip() if len(cells) > 0 else None
            # Get the text of the second cell
            change = cells[1].text.strip() if len(cells) > 1 else None
            # Get the text of the third cell
            bubble = cells[2].text.strip() if len(cells) > 2 else ""
            # Split the bubble into amount and percentage
            bubble_amount, bubble_percent = self._split_bubble(bubble)

            coins.append(
                {
                    "title": self._coin_titles.get(title, title),
                    "price": price,
                    "change": change,
                    "bubble_amount": bubble_amount,
                    "bubble_percentage": bubble_percent,
                }
            )

        last_update = self.extract_last_update(soup)

        result = {
            "last_update": last_update,
            "coins": coins,
        }

        if format == "json":
            return json.dumps(result, ensure_ascii=False, indent=4)

        return result

    def _split_bubble(self, bubble: str) -> tuple[str, str]:
        """
        Splits the bubble into amount and percentage.
        """
        # Check if the bubble contains a percentage
        if "%" in bubble:
            # Split the bubble into amount and percentage
            amount, percent = bubble.split("%")
            # Return the amount and percentage
            return amount.strip(), percent.strip() + "%"
        return "", ""
