from typing import Protocol

from kakeibo.google_sheet import GoogleSheetProtocol
from kakeibo.slack import SlackMessage, SlackMessageBuilderProtocol


class KakeiboServiceProtocol(Protocol):
    def get_slack_messages(self) -> list[SlackMessage]: ...

    def write_google_sheet(self, slack_messages: list[SlackMessage]) -> None: ...


class KakeiboService:
    def __init__(
        self, slack_message_builder: SlackMessageBuilderProtocol, google_sheet_client: GoogleSheetProtocol
    ) -> None:
        self.slack_message_builder = slack_message_builder
        self.google_sheet_client = google_sheet_client

    def get_slack_messages(self) -> list[SlackMessage]:
        return self.slack_message_builder.build()

    def write_google_sheet(self, slack_messages: list[SlackMessage]) -> None:
        self.google_sheet_client.write(slack_messages)
