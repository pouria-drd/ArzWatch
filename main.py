import os
from dotenv import load_dotenv
from fetchers import TGJUPriceFetcher
from formatters.tgju import TGJUPriceFormatter, TGJUTablePrinter
from utils.tgju_print_helpers import tgju_print_name_value, tgju_print_price_table

# Loads the variables from the .env file into the environment
load_dotenv()

# True to use Toman, False to use Rial
use_toman = os.getenv("USE_TOMAN", "True") == "True"
# table or name_value
print_type = os.getenv("PRINT_TYPE", "table")


def main():
    fetcher = TGJUPriceFetcher()
    formatter = TGJUPriceFormatter(use_toman=use_toman)
    table_printer = TGJUTablePrinter()

    data = fetcher.fetch_data()

    if "error" in data:
        print("❌ Error:", data["error"])
    else:
        if print_type == "table":
            flat_prices = formatter.flatten_and_format(data)
            tgju_print_price_table(table_printer, flat_prices)
        elif print_type == "name_value":
            flat_prices = formatter.flatten_and_format(data)
            tgju_print_name_value(flat_prices)


if __name__ == "__main__":
    main()
