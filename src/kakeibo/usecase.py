from kakeibo.service import KakeiboService


class KakeiboUseCase:
    def __init__(self, kakeibo_service: KakeiboService) -> None:
        self.kakeibo_service = kakeibo_service

    def execute(self) -> None:
        slack_messages = self.kakeibo_service.get_slack_messages()
        self.kakeibo_service.write_google_sheet(slack_messages)
