from typing import Protocol

from kakeibo.google_sheet import GoogleSheetProtocol
from kakeibo.slack import SlackMessage, SlackProtocol


class KakeiboServiceProtocol(Protocol):
    def get_slack_messages(self) -> list[SlackMessage]: ...

    def write_google_sheet(self, slack_messages: list[SlackMessage]) -> None: ...


class KakeiboService:
    def __init__(self, slack_client: SlackProtocol, google_sheet_client: GoogleSheetProtocol) -> None:
        self.slack_client = slack_client
        self.google_sheet_client = google_sheet_client

    def get_slack_messages(self) -> list[SlackMessage]:
        return self.slack_client.get()

    def write_google_sheet(self, slack_messages: list[SlackMessage]) -> None:
        self.google_sheet_client.write(slack_messages)
