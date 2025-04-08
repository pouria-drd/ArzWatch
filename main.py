from extractors.alan_chand import GoldAndCoinExtractor


def main():
    extractor = GoldAndCoinExtractor()
    # print(extractor.extract_data())
    print(extractor.extract_data(format="json"))
    # print(extractor.extract_gold_data(format="json"))
    # print(extractor.extract_coin_data(format="json"))


if __name__ == "__main__":
    main()
