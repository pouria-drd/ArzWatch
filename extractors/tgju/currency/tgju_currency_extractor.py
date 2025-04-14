from logger import LoggerFactory
from extractors.tgju.base import TGJUBaseExtractor


class TGJUCurrencyExtractor(TGJUBaseExtractor):
    def __init__(self):
        super().__init__(
            url="https://www.tgju.org/currency",
            logger=LoggerFactory.get_logger(
                "TGJUCurrencyExtractor", "extractors/tgju/currency"
            ),
        )

    def _is_relevant_row(self, row) -> bool:
        titles = [
            "دلار",
            "یورو",
            "یوان چین",
            "درهم امارات",
            "پوند انگلیس",
            "لیر ترکیه",
            "روبل روسیه",
        ]
        title = row.find("th").text.strip()
        return title in titles
