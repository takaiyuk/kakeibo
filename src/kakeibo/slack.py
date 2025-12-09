from datetime import datetime
from typing import Any, Final, Protocol

import requests
from pydantic import BaseModel

from kakeibo.config import Config

USER_BOT: Final = "USLACKBOT"


class SlackAlertMessage(BaseModel):
    message: str


class SlackAlertProtocol(Protocol):
    def send(self, messages: list[SlackAlertMessage]) -> None: ...


class SlackAlert:
    def __init__(self, config: Config) -> None:
        self.config = config

    def send(self, messages: list[SlackAlertMessage]) -> None:
        url = "https://slack.com/api/chat.postMessage"
        header = {"Authorization": f"Bearer {self.config.slack_token}"}
        joined_message = "\n".join([msg.message for msg in messages])
        payload = {
            "channel": self.config.slack_alert_channel_id,
            "text": joined_message,
        }
        requests.post(url=url, headers=header, json=payload)


class Interval(BaseModel):
    days: int = 0
    minutes: int = 10

    def convert_minutes(self) -> int:
        return self.days * 24 * 60 + self.minutes


class FilterCondition(BaseModel):
    exclude_interval: Interval | None = None


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
        self.slack_messages = filtered_slack_messages

    def transform(self) -> None:
        transformed_messages: list[SlackMessage] = []
        for message in self.slack_messages:
            if message.has_newline():
                split_messages = message.text.split("\n")
                new_messages: list[SlackMessage] = [
                    # NOTE: ts に微小な差分をつけてユニークにする
                    SlackMessage(ts=message.ts + i * 1e-6, text=text, user=message.user)
                    for i, text in enumerate(split_messages)
                ]
                new_messages.sort(key=lambda msg: msg.ts)
                new_messages.reverse()  # NOTE: 元が新しい順なので逆順にする
                transformed_messages.extend(new_messages)
            else:
                transformed_messages.append(message)
        self.slack_messages = transformed_messages

    def complement(self, logger: Any, config: Config) -> list[SlackAlertMessage]:
        slack_alert_messages: list[SlackAlertMessage] = []
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
                                msg = f"Slack message user is invalid: {message.user}"
                                logger.warning(msg)
                                slack_alert_messages.append(SlackAlertMessage(message=msg))
                case 3:
                    pass
                case _:
                    msg = f"Slack message format is invalid: {message.text}"
                    logger.warning(msg)
                    slack_alert_messages.append(SlackAlertMessage(message=msg))
                    pass
            new_slack_messages.append(message)
        self.slack_messages = new_slack_messages
        return slack_alert_messages

    def sort(self) -> None:
        self.slack_messages.sort(key=lambda message: message.ts)


class SlackMessageBuilderProtocol(Protocol):
    def build(self) -> list[SlackMessage]: ...


class SlackMessageBuilder:
    def __init__(
        self, logger: Any, config: Config, filter_condition: FilterCondition, slack_alert_client: SlackAlertProtocol
    ) -> None:
        self.logger = logger
        self.config = config
        self.filter_condition = filter_condition
        self.slack_alert_client = slack_alert_client

    def _fetch(self) -> list[dict[str, str]]:
        url = "https://slack.com/api/conversations.history"
        header = {"Authorization": f"Bearer {self.config.slack_token}"}
        payload = {"channel": self.config.slack_channel_id}
        response = requests.get(url=url, headers=header, params=payload)
        messages = response.json().get("messages")
        return messages

    def build(self) -> list[SlackMessage]:
        messages = self._fetch()
        slack_messages = SlackMessages.build(messages)
        if self.filter_condition.exclude_interval is not None:
            slack_messages.filter(self.filter_condition.exclude_interval)
        slack_messages.transform()
        slack_alert_messages = slack_messages.complement(self.logger, self.config)
        if slack_alert_messages:
            self.slack_alert_client.send(slack_alert_messages)
        slack_messages.sort()
        return slack_messages.slack_messages
