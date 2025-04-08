from tabulate import tabulate


class TGJUTablePrinter:
    """
    A class to print formatted prices in a table format.
    """

    def __init__(self, headers=["Name", "Price"]):
        self.headers = headers

    def print_table(self, formatted_data):
        """
        Prints a table of already-formatted (colored) names and prices.

        Args:
            formatted_data (dict): Colored name: colored price dict from TGJUPriceFormatter.flatten_and_format
        """
        table_data = []

        for colored_name, colored_price in formatted_data.items():
            table_data.append([colored_name, colored_price])

        print(tabulate(table_data, headers=self.headers, tablefmt="grid"))
