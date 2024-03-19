from kakeibo.service import KakeiboService
from kakeibo.slack import Interval


class KakeiboUseCase:
    def __init__(self, kakeibo_service: KakeiboService) -> None:
        self.kakeibo_service = kakeibo_service

    def execute(self, interval: Interval) -> None:
        slack_messages = self.kakeibo_service.get_slack_messages(interval)
        self.kakeibo_service.write_google_sheet(slack_messages)
