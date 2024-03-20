from kakeibo.google_sheet import GoogleSheet
from kakeibo.slack import Slack, SlackMessage


class KakeiboService:
    def __init__(self, slack_client: Slack, google_sheet_client: GoogleSheet) -> None:
        self.slack_client = slack_client
        self.google_sheet_client = google_sheet_client

    def get_slack_messages(self) -> list[SlackMessage]:
        return self.slack_client.get()

    def write_google_sheet(self, slack_messages: list[SlackMessage]) -> None:
        self.google_sheet_client.write(slack_messages)
