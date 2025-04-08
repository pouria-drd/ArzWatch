import requests
from bs4 import BeautifulSoup


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
            # Get the response from the website
            response = requests.get(self.url)
            # Raise an exception if the response is not successful
            response.raise_for_status()
            # Return the BeautifulSoup object
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Error fetching data from {self.url}: {e}")
            raise

    def extract_last_update(self, soup: BeautifulSoup) -> str:
        """
        Extracts the last update from the website.
        """
        # Find the p tag with class "text-center"
        update_tag = soup.find("p", class_="text-center")
        # Check if the update tag exists
        if update_tag and "آخرین بروز رسانی" in update_tag.text:
            # Return the text without the prefix
            return update_tag.text.replace("آخرین بروز رسانی : ", "").strip()
        return ""
