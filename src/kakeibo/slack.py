from datetime import datetime

import requests
from pydantic import BaseModel

from kakeibo.config import Config


class Interval(BaseModel):
    days: int = 0
    minutes: int = 10

    def convert_minutes(self) -> int:
        return self.days * 24 * 60 + self.minutes


class SlackMessage(BaseModel):
    ts: float
    text: str


class SlackMessages(BaseModel):
    slack_messages: list[SlackMessage]

    @classmethod
    def build(cls, messages: list[dict[str, str]]) -> "SlackMessages":
        return cls(slack_messages=[SlackMessage(ts=float(message["ts"]), text=message["text"]) for message in messages])

    def filter(
        self,
        exclude_interval: Interval,
        is_sort: bool,
    ) -> None:
        dt_now = datetime.now()
        filtered_slack_messages: list[SlackMessage] = []
        for message in self.slack_messages:
            dt_message = datetime.fromtimestamp(message.ts)
            diff_days = (dt_now - dt_message).days
            diff_minutes = (dt_now - dt_message).seconds / 60
            # 10分毎に実行されるので、10分より前のメッセージは除外する
            if diff_days * 24 * 60 + diff_minutes > exclude_interval.convert_minutes():
                break
            filtered_slack_messages.append(message)
        if is_sort:
            filtered_slack_messages = filtered_slack_messages[::-1]
        self.slack_messages = filtered_slack_messages


class Slack:
    def __init__(self, config: Config) -> None:
        self.config = config

    def _fetch(self) -> list[dict[str, str]]:
        url = "https://slack.com/api/conversations.history"
        header = {"Authorization": f"Bearer {self.config.slack_token}"}
        payload = {"channel": self.config.slack_channel_id}
        response = requests.get(url=url, headers=header, params=payload)
        messages = response.json().get("messages")
        return messages

    def get(self, exclude_interval: Interval | None, is_sort: bool = True) -> list[SlackMessage]:
        messages = self._fetch()
        slack_messages = SlackMessages.build(messages)
        if exclude_interval is None:
            return slack_messages.slack_messages
        slack_messages.filter(exclude_interval, is_sort)
        return slack_messages.slack_messages
