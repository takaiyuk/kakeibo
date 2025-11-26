from datetime import datetime
from typing import Any, Final, Protocol

import requests
from pydantic import BaseModel

from kakeibo.config import Config

USER_BOT: Final = "USLACKBOT"


class Interval(BaseModel):
    days: int = 0
    minutes: int = 10

    def convert_minutes(self) -> int:
        return self.days * 24 * 60 + self.minutes


class FilterCondition(BaseModel):
    exclude_interval: Interval | None = None
    is_sort: bool = True


class SlackMessage(BaseModel):
    ts: float
    text: str
    user: str

    # text に \n が含まれるかを確認する
    def has_newline(self) -> bool:
        return "\n" in self.text


class SlackMessages(BaseModel):
    slack_messages: list[SlackMessage]

    @classmethod
    def build(cls, messages: list[dict[str, str]]) -> "SlackMessages":
        return cls(
            slack_messages=[
                SlackMessage(ts=float(message["ts"]), text=message["text"], user=message["user"])
                for message in messages
            ]
        )

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
            # `[ignore]` で始まるメッセージは除外する
            if message.text.startswith("[ignore]"):
                continue
            filtered_slack_messages.append(message)
        if is_sort:
            filtered_slack_messages = filtered_slack_messages[::-1]
        self.slack_messages = filtered_slack_messages

    def transform(self) -> None:
        transformed_messages: list[SlackMessage] = []
        for message in self.slack_messages:
            if message.has_newline():
                split_messages = message.text.split("\n")
                split_messages = split_messages[::-1]  # 元が新しい順なので逆順にする
                new_messages: list[SlackMessage] = [
                    SlackMessage(ts=message.ts, text=text, user=message.user) for text in split_messages
                ]
                transformed_messages.extend(new_messages)
            else:
                transformed_messages.append(message)
        self.slack_messages = transformed_messages

    def complement(self, logger: Any, config: Config) -> None:
        new_slack_messages: list[SlackMessage] = []
        for message in self.slack_messages:
            match len(message.text.split(",")):
                case 2:
                    # 特殊ルール: メッセージのアイテム数が2の場合、userがUSER1の場合は末尾に`,1`を、userがUSER2の場合は末尾に`,4`を追加する
                    match message.user:
                        case config.slack_user1:
                            message.text += ",1"
                        case config.slack_user2:
                            message.text += ",4"
                        case _:
                            if message.user != USER_BOT:
                                logger.warning(f"Slack message user is invalid: {message.user}")
                case 3:
                    pass
                case _:
                    logger.warning(f"Slack message format is invalid: {message.text}")
                    pass
            new_slack_messages.append(message)
        self.slack_messages = new_slack_messages


class SlackProtocol(Protocol):
    def get(self) -> list[SlackMessage]: ...


class Slack:
    def __init__(self, logger: Any, config: Config, filter_condition: FilterCondition) -> None:
        self.logger = logger
        self.config = config
        self.filter_condition = filter_condition

    def _fetch(self) -> list[dict[str, str]]:
        url = "https://slack.com/api/conversations.history"
        header = {"Authorization": f"Bearer {self.config.slack_token}"}
        payload = {"channel": self.config.slack_channel_id}
        response = requests.get(url=url, headers=header, params=payload)
        messages = response.json().get("messages")
        return messages

    def get(self) -> list[SlackMessage]:
        messages = self._fetch()
        slack_messages = SlackMessages.build(messages)
        if self.filter_condition.exclude_interval is None:
            return slack_messages.slack_messages
        slack_messages.filter(self.filter_condition.exclude_interval, self.filter_condition.is_sort)
        slack_messages.transform()
        slack_messages.complement(self.logger, self.config)
        return slack_messages.slack_messages
