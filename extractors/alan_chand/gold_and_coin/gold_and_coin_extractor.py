import json
from typing import List, Dict, Optional
from .gold_extractor import GoldExtractor
from .coin_extractor import CoinExtractor


class GoldAndCoinExtractor:
    """
    Extracts gold and coin data from the https://alanchand.com/gold-price website.
    """

    def __init__(self):
        self.gold_extractor = GoldExtractor()
        self.coin_extractor = CoinExtractor()

    def extract_data(self, format: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Extracts gold and coin data from the https://alanchand.com/gold-price website.

        Args:
            format: The format of the data to be returned. (json)

        Returns:
            The gold and coin data.
        """
        # Get the BeautifulSoup object
        soup = self.gold_extractor.fetch_data()
        # Extract the gold data
        gold_data = self.gold_extractor.extract_gold_data(soup)
        # Extract the coin data
        coin_data = self.coin_extractor.extract_coin_data(soup)

        result = {
            "last_update": gold_data.get("last_update") or coin_data.get("last_update"),
            "golds": gold_data["golds"],
            "coins": coin_data["coins"],
        }

        if format == "json":
            return json.dumps(result, ensure_ascii=False, indent=4)

        return result

    def extract_gold_data(self, format: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Extracts gold data from the https://alanchand.com/gold-price website.

        Args:
            format: The format of the data to be returned. (json)

        Returns:
            The gold data.
        """
        # Get the BeautifulSoup object
        soup = self.gold_extractor.fetch_data()
        return self.gold_extractor.extract_gold_data(soup, format)

    def extract_coin_data(self, format: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Extracts coin data from the https://alanchand.com/gold-price website.

        Args:
            format: The format of the data to be returned. (json)

        Returns:
            The coin data.
        """
        # Get the BeautifulSoup object
        soup = self.coin_extractor.fetch_data()
        return self.coin_extractor.extract_coin_data(soup, format)
