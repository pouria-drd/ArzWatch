from bots import ArzWatchBot

# from scrapers.alan_chand import AlanChandGoldScraper, AlanChandCoinScraper


def main():
    bot = ArzWatchBot()
    bot.run()
    # gold_scraper = AlanChandGoldScraper()
    # result = gold_scraper.fetch_gold_data(pretty=True)
    # print(result)

    # coin_scraper = AlanChandCoinScraper()
    # result = coin_scraper.fetch_coin_data(pretty=True)
    # print(result)


if __name__ == "__main__":
    main()
