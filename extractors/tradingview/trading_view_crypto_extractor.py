import json
import requests
from bs4 import BeautifulSoup
from logger import LoggerFactory

# Create a logger for the extractor class
logger = LoggerFactory.get_logger(
    "TradingViewCryptoExtractor", "extractors/tradingview/crypto"
)


class TradingViewCryptoExtractor:
    """
    Scrapes cryptocurrency prices from https://tradingview.com/.
    """

    _SOURCE_URL: str = (
        "https://www.tradingview.com/markets/cryptocurrencies/prices-all/"
    )

    _PERSIAN_TO_ENGLISH_TITLES: dict[str, str] = {
        "بیت‌کوین": "Bitcoin",
        "اتریوم": "Ethereum",
        "ریپل": "Ripple",
        "لایت‌کوین": "Litecoin",
        # Add more cryptocurrencies here...
    }

    _ENGLISH_TO_PERSIAN_TITLES: dict[str, str] = {
        "Bitcoin": "بیت‌کوین",
        "Ethereum": "اتریوم",
        "Ripple": "ریپل",
        "Litecoin": "لایت‌کوین",
        # Add more cryptocurrencies here...
    }

    def get_pte_crypto_title_map(self) -> dict[str, str]:
        """
        Returns a dictionary that maps Persian titles to English titles.

        Returns:
            dict: A dictionary that maps Persian titles to English titles.
        """
        return self._PERSIAN_TO_ENGLISH_TITLES

    def get_etp_crypto_title_map(self) -> dict[str, str]:
        """
        Returns a dictionary that maps English titles to Persian titles.

        Returns:
            dict: A dictionary that maps English titles to Persian titles.
        """
        return self._ENGLISH_TO_PERSIAN_TITLES

    def fetch_crypto_data(self, pretty: bool = False) -> dict[str, str] | str | None:
        """
        Fetches and parses cryptocurrency data from the source URL.

        Args:
            pretty (bool): If True, returns the result as a pretty-printed JSON string.

        Returns:
            dict or str or None: Parsed cryptocurrency data or None if request fails.
        """
        try:
            # Get the response from the website with a timeout to avoid hanging
            response = requests.get(self._SOURCE_URL, timeout=7)
            # Raise an exception if the response status code is not 200
            response.raise_for_status()
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            # Parse the crypto data from the HTML content
            result = self._parse_crypto_data(soup)
            # Log a success message
            logger.info("Crypto data fetched successfully.")
            # Return the result as a JSON string if pretty is True, otherwise return the result
            if pretty:
                return (
                    json.dumps(result, ensure_ascii=False, indent=4)
                    if pretty
                    else result
                )
            return result
        except requests.RequestException as e:
            # Log an error message with the exception details
            logger.error(f"Failed to fetch data from {self._SOURCE_URL}: {e}")
            return None

    def _parse_crypto_data(self, soup: BeautifulSoup) -> dict[str, str]:
        """
        Parses cryptocurrency price data and last update time from HTML soup.

        Args:
            soup (BeautifulSoup): Parsed HTML soup.

        Returns:
            dict: Dictionary containing crypto prices and last update timestamp.
        """
        # Find all rows with class "crypto-row" or any other class that identifies crypto data rows
        data_rows = soup.find_all("div", class_="crypto-row")
        # Initialize an empty list to store crypto items
        crypto_items = []
        # Iterate over each row
        for row in data_rows:
            # Parse a single crypto item from the row
            item = self._parse_single_crypto_item(row)
            # Add the item to the crypto_items list if it's not None
            if item:
                crypto_items.append(item)
        # Get the last update timestamp from the HTML soup
        last_update_time = self._get_last_update_timestamp(soup)
        # Return a dictionary containing the crypto items and last update timestamp
        return {
            "cryptos": crypto_items,
            "last_update": last_update_time,
        }

    def _parse_single_crypto_item(self, row: BeautifulSoup) -> dict[str, str] | None:
        """
        Parses a single item row for cryptocurrency data.

        Args:
            row (BeautifulSoup): The row to parse.

        Returns:
            dict or None: The parsed crypto item data, or None if the row is empty or missing a title.
        """
        # Find the title tag
        title_tag = row.find("div", class_="crypto-name")
        # Check if the title tag is not empty
        if not title_tag:
            return None
        # Get the raw title text
        raw_title = title_tag.get_text(strip=True)
        # Get the English title from the raw title using the dictionary
        english_title = self.get_pte_crypto_title_map().get(raw_title)
        # Check if the English title is not empty
        if not english_title:
            return None
        # Find all cells in the row (price, change, etc.)
        cell_tags = row.find_all("div", class_="crypto-cell")
        # Get the price text
        price = cell_tags[0].get_text(strip=True) if len(cell_tags) > 0 else "N/A"
        # Get the change text
        change = cell_tags[1].get_text(strip=True) if len(cell_tags) > 1 else "N/A"
        # Get the bubble text
        bubble = cell_tags[2].get_text(strip=True) if len(cell_tags) > 2 else "N/A"
        # Split the bubble text into amount and percentage
        bubble_amount, bubble_percent = self._split_bubble_info(bubble)
        # Return a dictionary containing the crypto item data
        return {
            "title": english_title,
            "price": price,
            "change": change,
            "bubble_amount": bubble_amount or "N/A",
            "bubble_percentage": bubble_percent or "N/A",
        }

    def _split_bubble_info(self, bubble: str) -> tuple[str, str]:
        """
        Splits a bubble string into amount and percentage.

        Args:
            bubble (str): The bubble string to split.

        Returns:
            tuple: A tuple containing the amount and percentage.
        """
        if "%" in bubble:
            parts = bubble.split("%")
            amount = parts[0].strip()
            percentage = parts[1].strip()
            return amount, percentage + "%"
        return "", ""

    def _get_last_update_timestamp(self, soup: BeautifulSoup) -> str:
        """
        Extracts the last update timestamp from the page.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object.

        Returns:
            str: The last update timestamp.
        """
        # Find the last update tag
        update_tag = soup.find("p", class_="last-update")
        if update_tag:
            return update_tag.text.strip()
        return "Unknown"
