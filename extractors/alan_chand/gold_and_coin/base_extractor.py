import logging
import requests
from bs4 import BeautifulSoup

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseExtractor:
    """
    Base class for extracting gold and coin data from https://alanchand.com/gold-price website.
    """

    def __init__(self, url: str = "https://alanchand.com/gold-price"):
        self.url = url

    def fetch_data(self) -> BeautifulSoup:
        """
        Fetches the data from the website.
        """
        try:
            # Get the response from the website with a timeout to avoid hanging
            response = requests.get(self.url, timeout=5)
            response.raise_for_status()
            # Return the BeautifulSoup object
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {self.url}: {e}")
            raise

    def extract_last_update(self, soup: BeautifulSoup) -> str:
        """
        Extracts the last update from the website.
        """
        # Find the p tag with class "text-center"
        update_tag = soup.find("p", class_="text-center")
        if update_tag and "آخرین بروز رسانی" in update_tag.text:
            return update_tag.text.replace("آخرین بروز رسانی : ", "").strip()
        return ""
