from logger import LoggerFactory
from extractors.tgju.base import TGJUBaseExtractor


class TGJUGoldExtractor(TGJUBaseExtractor):
    def __init__(self):
        super().__init__(
            url="https://www.tgju.org/gold-chart",
            logger=LoggerFactory.get_logger(
                "TGJUGoldExtractor", "extractors/tgju/gold"
            ),
        )

    def _is_relevant_row(self, row) -> bool:
        titles = ["طلای 18 عیار / 750", "مثقال طلا"]
        title = row.find("th").text.strip()
        return title in titles
