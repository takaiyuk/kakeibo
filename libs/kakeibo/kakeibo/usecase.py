from kakeibo.service import KakeiboServiceProtocol


class KakeiboUseCase:
    def __init__(self, kakeibo_service: KakeiboServiceProtocol) -> None:
        self.kakeibo_service = kakeibo_service

    def execute(self) -> None:
        slack_messages = self.kakeibo_service.get_slack_messages()
        self.kakeibo_service.write_google_sheet(slack_messages)
