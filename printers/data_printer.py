from typing import Dict
from tabulate import tabulate
from termcolor import colored
import shutil


class DataPrinter:
    """
    A utility class to format and print pricing data in a tabular format.
    It supports colorized output using the 'termcolor' library and displays the last update time centered below the table.
    """

    def __init__(self, data: Dict):
        """
        Initialize the printer with data.

        Args:
            data (Dict): A dictionary containing the keys 'golds' or 'coins', and optionally 'last_update'.
        """
        self.data = data
        self.last_update = self.data.get("last_update", "N/A")

    def print_table(self) -> None:
        """
        Prints the extracted data (gold or coin) in a formatted table using the tabulate library.
        The table includes color-coded fields for better readability.
        A separate footer line with the last update timestamp is displayed centered below the table.
        """

        # Define column headers with color
        headers = [
            colored("Title", "cyan", attrs=["bold"]),
            colored("Price", "cyan", attrs=["bold"]),
            colored("Change", "cyan", attrs=["bold"]),
            colored("Bubble Amount", "cyan", attrs=["bold"]),
            colored("Bubble Percentage", "cyan", attrs=["bold"]),
        ]

        # Extract gold or coin items from the data
        items = self.data.get("golds") or self.data.get("coins") or []

        rows = []
        for item in items:
            title = colored(item["title"], "yellow")
            price = colored(item["price"], "green") if item["price"] else "N/A"
            change = colored(item["change"], "light_blue")

            # Colorize the bubble amount and percentage
            bubble_amount = (
                self._negative_positive_color(item["bubble_amount"])
                if item["bubble_amount"]
                else "N/A"
            )
            bubble_percentage = (
                self._negative_positive_color(item["bubble_percentage"])
                if item["bubble_percentage"]
                else "N/A"
            )

            # Append the row to the table
            rows.append([title, price, change, bubble_amount, bubble_percentage])

        # Add a footer line with the last update timestamp
        footer_text = colored(
            f"Last Update: {self.last_update}", "light_blue", attrs=["bold"]
        )
        rows.append(
            [footer_text] + [""] * (len(headers) - 1)
        )  # Add an empty column for spacing

        # Print the table
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

    def _negative_positive_color(self, text: str) -> str:
        """
        Determines the color of a value based on whether it is negative or positive.

        Args:
            text (str): The text to evaluate (e.g. a number like "-250" or "120").

        Returns:
            str: A colored string based on the value's sign.
        """
        if text.startswith("-"):
            return colored(text, "red")  # Negative values in red
        if "N/A" in text:
            return colored(text, "white")  # Missing values in white
        return colored(text, "green")  # Positive or neutral values in green
