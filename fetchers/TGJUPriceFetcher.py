import requests
from bs4 import BeautifulSoup


class TGJUPriceFetcher:
    """
    A class that handles fetching live exchange rates and commodity prices.
    """

    currency_ids = {
        "dollar": "l-price_dollar_rl",
    }

    gold_ids = {
        "gold_ounce": "l-ons",
        "gold_mesghal": "l-mesghal",
        "gold_18": "l-geram18",
        "coin": "l-sekee",
    }

    crypto_ids = {
        "tether": "l-crypto-tether-irr",
        "bitcoin": "l-crypto-bitcoin",
    }

    stock_ids = {
        "stock": "l-gc30",
    }

    oil_ids = {
        "oil_brent": "l-oil_brent",
    }

    def __init__(self, url="https://www.tgju.org/"):
        self.url = url

    def fetch_data(self):
        """
        Fetches and returns live prices from the TGJU website.

        Returns:
            dict: A dictionary containing extracted prices or an error message.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # This will raise an exception if the status is not 200

            soup = BeautifulSoup(response.text, "html.parser")
            return self._extract_all_prices(soup)

        except requests.exceptions.RequestException as e:
            return {"error": f"Request error: {e}"}

    def _get_price_element(self, soup, price_id):
        """
        Finds the price element in the soup using the provided price ID.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            price_id (str): ID of the price element to find.

        Returns:
            bs4.element.Tag: The price element if found, otherwise None.
        """
        price_element = soup.find("li", {"id": price_id})
        if price_element:
            return price_element
        else:
            return None

    def _get_price_value(self, price_element):
        """
        Extracts the price value from the price element.

        Args:
            price_element (bs4.element.Tag): The price element to extract the value from.

        Returns:
            str: The price value if found, otherwise "Not available".
        """
        price_value = price_element.find("span", {"class": "info-price"})
        if price_value:
            return price_value.text.strip()
        else:
            return "Not available"

    def _extract_price(self, soup, price_id):
        """
        Extracts the price value from the price element.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            price_id (str): ID of the price element to extract the value from.

        Returns:
            str: The price value if found, otherwise "Not available".
        """
        price_element = self._get_price_element(soup, price_id)
        if price_element:
            return self._get_price_value(price_element)
        else:
            return "Not available"

    def _extract_currency_prices(self, soup):
        """
        Extracts the price value from the price element.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            dict: A dictionary containing extracted prices.
        """
        prices = {}
        for key, price_id in self.currency_ids.items():
            prices[key] = self._extract_price(soup, price_id)
        return prices

    def _extract_gold_prices(self, soup):
        """
        Extracts the price value from the price element.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            dict: A dictionary containing extracted prices.
        """
        prices = {}
        for key, price_id in self.gold_ids.items():
            prices[key] = self._extract_price(soup, price_id)
        return prices

    def _extract_crypto_prices(self, soup):
        """
        Extracts the price value from the price element.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            dict: A dictionary containing extracted prices.
        """
        prices = {}
        for key, price_id in self.crypto_ids.items():
            prices[key] = self._extract_price(soup, price_id)
        return prices

    def _extract_stock_prices(self, soup):
        """
        Extracts the price value from the price element.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            dict: A dictionary containing extracted prices.
        """
        prices = {}
        for key, price_id in self.stock_ids.items():
            prices[key] = self._extract_price(soup, price_id)
        return prices

    def _extract_oil_prices(self, soup):
        """
        Extracts the price value from the price element.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            dict: A dictionary containing extracted prices.
        """
        prices = {}
        for key, price_id in self.oil_ids.items():
            prices[key] = self._extract_price(soup, price_id)
        return prices

    def _extract_all_prices(self, soup):
        """
        Extracts all prices from the TGJU website.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            dict: A dictionary containing extracted prices.
        """
        prices = {}

        prices["oil"] = self._extract_oil_prices(soup)
        prices["stock"] = self._extract_stock_prices(soup)

        prices["gold"] = self._extract_gold_prices(soup)
        prices["crypto"] = self._extract_crypto_prices(soup)
        prices["currency"] = self._extract_currency_prices(soup)

        return prices
