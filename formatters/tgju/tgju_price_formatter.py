from termcolor import colored


class TGJUPriceFormatter:
    """
    A class for formatting and converting nested price dictionaries
    into flat readable versions with color per category.
    """

    readable_names = {
        "dollar": "Dollar",
        "gold_ounce": "Gold Ounce",
        "gold_mesghal": "Gold Mesghal",
        "gold_18": "Gold 18K",
        "coin": "Coin",
        "tether": "Tether",
        "bitcoin": "Bitcoin",
        "stock": "Stock",
        "oil_brent": "Brent Oil",
    }

    category_colors = {
        "currency": "red",
        "gold": "yellow",
        "crypto": "blue",
        "stock": "light_cyan",
        "oil": "black",
    }

    usd_keys = ["gold_ounce", "bitcoin", "oil_brent"]

    def __init__(self, use_toman=True):
        self.use_toman = use_toman

    def flatten_and_format(self, nested_data):
        """
        Flattens and formats nested price data into a clean dict.

        Args:
            nested_data (dict): Nested dict from TGJUPriceFetcher.fetch_data()

        Returns:
            dict: A flat dict with colored titles and green prices.
        """
        flat_data = {}

        for category, values in nested_data.items():
            color = self.category_colors.get(category, "white")

            for key, raw_value in values.items():
                name = self.readable_names.get(key, key)

                if self.use_toman and key not in self.usd_keys:
                    raw_value = self._convert_rial_to_toman(raw_value)

                symbol = self._get_currency_symbol(key)
                formatted_price = self._format_value(raw_value)

                # Colorize title and price separately
                colored_name = colored(name, color, attrs=["bold"])
                colored_price = colored(f"{formatted_price} {symbol}", "green")

                flat_data[colored_name] = colored_price

        return flat_data

    def _get_currency_symbol(self, key):
        """
        Returns the currency symbol based on the key type and setting.
        """
        if key in self.usd_keys:
            return "$"
        return "IRT" if self.use_toman else "IRR"

    def _format_value(self, value):
        """
        Formats a numeric string with commas and appropriate decimal formatting.
        """
        try:
            cleaned = value.replace(",", "")
            if "." in cleaned:
                return f"{float(cleaned):,.2f}"
            return f"{int(cleaned):,}"
        except Exception:
            return value

    def _convert_rial_to_toman(self, value):
        """
        Converts a Rial value string to Toman by removing the last zero.

        Args:
            value (str): Raw price in Rials

        Returns:
            str: Price in Tomans
        """
        try:
            cleaned = value.replace(",", "")
            toman = int(cleaned) // 10
            return str(toman)
        except Exception:
            return value
