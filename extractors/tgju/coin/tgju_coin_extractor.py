from logger import LoggerFactory
from extractors.tgju.base import TGJUBaseExtractor


class TGJUCoinExtractor(TGJUBaseExtractor):
    def __init__(self):
        super().__init__(
            url="https://www.tgju.org/coin",
            logger=LoggerFactory.get_logger(
                "TGJUCoinExtractor", "extractors/tgju/coin"
            ),
        )

    def _is_relevant_row(self, row) -> bool:
        titles = ["ربع سکه", "نیم سکه", "سکه امامی", "سکه بهار آزادی"]
        title = row.find("th").text.strip()
        return title in titles
