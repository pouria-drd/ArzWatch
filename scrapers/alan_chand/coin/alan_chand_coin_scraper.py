import json
import requests
from bs4 import BeautifulSoup
from logger import LoggerFactory

# Create a logger for the scraper class
logger = LoggerFactory.get_logger("AlanChandCoinScraper", "scrapers/alan_chand/coin")


class AlanChandCoinScraper:
    """
    Scrapes coin prices from https://alanchand.com/gold-price.
    """

    _SOURCE_URL: str = "https://alanchand.com/gold-price"

    _PERSIAN_TO_ENGLISH_TITLES: dict[str, str] = {
        "سکه امامی": "Imami Coin",
        "سکه بهار آزادی": "Bahare Azadi Coin",
        "نیم سکه": "Half Coin",
        "ربع سکه": "Quarter Coin",
        "سکه گرمی": "Gram Coin",
    }

    _ENGLISH_TO_PERSIAN_TITLES: dict[str, str] = {
        "Imami Coin": "سکه امامی",
        "Bahare Azadi Coin": "سکه بهار آزادی",
        "Half Coin": "نیم سکه",
        "Quarter Coin": "ربع سکه",
        "Gram Coin": "سکه گرمی",
    }

    def get_pte_coin_title_map(self) -> dict[str, str]:
        """
        Returns a dictionary that maps Persian titles to English titles.

        Returns:
            dict: A dictionary that maps Persian titles to English titles.
        """
        return self._PERSIAN_TO_ENGLISH_TITLES

    def get_etp_coin_title_map(self) -> dict[str, str]:
        """
        Returns a dictionary that maps English titles to Persian titles.

        Returns:
            dict: A dictionary that maps English titles to Persian titles.
        """
        return self._ENGLISH_TO_PERSIAN_TITLES

    def fetch_coin_data(self, pretty: bool = False) -> dict[str, str] | str | None:
        """
        Fetches and parses coin data from the source URL.

        Args:
            pretty (bool): If True, returns the result as a pretty-printed JSON string.

        Returns:
            dict or str or None: Parsed coin data or None if request fails.
        """
        try:
            # Get the response from the website with a timeout to avoid hanging
            response = requests.get(self._SOURCE_URL, timeout=7)
            # Raise an exception if the response status code is not 200
            response.raise_for_status()
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            # Parse the coin data from the HTML content
            result = self._parse_coin_data(soup)
            # Log a success message
            logger.info("Coin data fetched successfully.")
            # Return the result as a JSON string if pretty is True, otherwise return the result
            return (
                json.dumps(result, ensure_ascii=False, indent=4) if pretty else result
            )
        # Handle any exceptions that may occur during the fetching process
        except requests.RequestException as e:
            # Log an error message with the exception details
            logger.error(f"Failed to fetch data from {self._SOURCE_URL}: {e}")
            return None

    def _parse_coin_data(self, soup: BeautifulSoup) -> dict[str, str]:
        """
        Parses coin price data and last update time from HTML soup.

        Args:
            soup (BeautifulSoup): Parsed HTML soup.

        Returns:
            dict: Dictionary containing coin prices and last update timestamp.
        """
        # Find all rows with class "col-lg-12"
        data_rows = soup.find_all("div", class_="col-lg-12")
        # Initialize an empty list to store coin items
        coin_items = []
        # Iterate over each row
        for row in data_rows:
            # Parse a single coin item from the row
            item = self._parse_single_item(row)
            # Add the item to the gold_items list if it's not None
            if item:
                coin_items.append(item)
        # Get the last update timestamp from the HTML soup
        last_update_time = self._get_last_update_timestamp(soup)
        # Return a dictionary containing the coin items and last update timestamp
        return {
            "coins": coin_items,
            "last_update": last_update_time,
        }

    def _parse_single_item(self, row: BeautifulSoup) -> dict[str, str] | None:
        """
        Parses a single item row.

        Args:
            row (BeautifulSoup): The row to parse.

        Returns:
            dict or None: The parsed item data, or None if the row is empty or missing a title.
        """
        # Find the title tag
        title_tag = row.find("div", class_="persian")
        # Check if the title tag is not empty
        if not title_tag:
            # Log a warning message
            logger.warning("Row skipped: Missing title.")
            return None
        # Get the raw title text
        raw_title = title_tag.get_text(strip=True)
        # Get the English title from the raw title
        english_title = self.get_pte_coin_title_map().get(raw_title)
        # Check if the English title is not empty
        if not english_title:
            # Log a warning message
            logger.warning(f"Unknown title skipped: '{raw_title}'")
            return None
        # Find all cells in the row
        cell_tags = row.find_all("div", class_="cell")
        # Get the price text
        price = cell_tags[0].get_text(strip=True) if len(cell_tags) > 0 else "N/A"
        # Get the change text
        change = cell_tags[1].get_text(strip=True) if len(cell_tags) > 1 else "N/A"
        # Get the bubble text
        bubble = cell_tags[2].get_text(strip=True) if len(cell_tags) > 2 else "N/A"
        # Split the bubble text into amount and percentage
        bubble_amount, bubble_percent = self._split_bubble_info(bubble)
        # Return a dictionary containing the coin item data
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
        # Check if the bubble string contains a percentage
        if "%" in bubble:
            # Split the bubble string into amount and percentage
            parts = bubble.split("%")
            # Get the amount and percentage
            amount = parts[0].strip()
            # Get the percentage
            percentage = parts[1].strip()
            # Return the amount and percentage
            return amount, percentage + "%"
        # Return an empty string for amount and percentage
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
        update_tag = soup.find("p", class_="text-center")
        # Check if the last update tag is not empty and contains the expected text
        if update_tag and "آخرین بروز رسانی" in update_tag.text:
            # Extract the last update timestamp from the text
            return update_tag.text.replace("آخرین بروز رسانی : ", "").strip()
        # Return an empty string if the last update tag is empty or does not contain the expected text
        return ""
