def tgju_print_name_value(flat_prices: dict):
    """
    Prints each key-value pair in a name: value format.

    Args:
        flat_prices (dict): A flat dictionary with colored name and value strings.
    """
    for name, value in flat_prices.items():
        print(f"{name}: {value}")


def tgju_print_price_table(table_printer, flat_prices: dict):
    """
    Prints the prices using a TablePrinter.

    Args:
        table_printer (TablePrinter): Instance of the table printer.
        flat_prices (dict): A flat dictionary with colored name and value strings.
    """
    table_printer.print_table(flat_prices)
