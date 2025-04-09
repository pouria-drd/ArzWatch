import sys
from printers import DataPrinter
from extractors.alan_chand import GoldAndCoinExtractor


def main():
    if len(sys.argv) < 2:
        print("Usage: py main.py [golds|coins]")
        return

    category = sys.argv[1]

    extractor = GoldAndCoinExtractor()

    if category == "golds":
        data = extractor.fetch_gold_data()
    elif category == "coins":
        data = extractor.fetch_coin_data()
    else:
        print("Invalid category. Use 'golds' or 'coins'.")
        return

    printer = DataPrinter(data)
    printer.print_table()


if __name__ == "__main__":
    main()
