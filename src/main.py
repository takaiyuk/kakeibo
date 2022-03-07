from dataclasses import dataclass
from datetime import datetime
from typing import Type, TypeVar

import requests

C = TypeVar("C", bound="Config")
S = TypeVar("S", bound="SlackMessage")


@dataclass
class Config:
    slack_token: str
    slack_channel_id: str
    ifttt_webhook_token: str
    ifttt_event_name: str

    @classmethod
    def build(cls: Type[C], env_dict: dict[str, str]) -> Type[C]:
        return cls(
            env_dict.get("SLACK_TOKEN"),
            slack_channel_id=env_dict.get("SLACK_CHANNEL_ID"),
            ifttt_webhook_token=env_dict.get("IFTTT_WEBHOOK_TOKEN"),
            ifttt_event_name=env_dict.get("IFTTT_EVENT_NAME"),
        )


@dataclass
class SlackMessage:
    ts: float
    text: str

    @classmethod
    def get(cls: Type[S], config: Type[C]) -> list[S]:
        url = "https://slack.com/api/conversations.history"
        token = config.slack_token
        header = {"Authorization": f"Bearer {token}"}
        channel_id = config.slack_channel_id
        payload = {"channel": channel_id}
        messages = cls._get_request_messages(url, header, payload)
        slack_messages = [
            cls(ts=float(message.get("ts")), text=message.get("text"))
            for message in messages
        ]
        return slack_messages

    @classmethod
    def filter(
        cls: Type[S],
        slack_messages: list[Type[S]],
        dt_now: datetime,
        exclude_days: int = 0,
        exclude_minutes: int = 10,
        is_sort: bool = True,
    ) -> list[Type[S]]:
        filtered_slack_messages: list[Type[S]] = []
        for message in slack_messages:
            dt_message = datetime.fromtimestamp(message.ts)
            diff_days = (dt_now - dt_message).days
            diff_minutes = (dt_now - dt_message).seconds / 60
            # 10分毎に実行されるので、10分より前のメッセージは除外する
            if diff_days > exclude_days or diff_minutes > exclude_minutes:
                break
            filtered_slack_messages.append(message)
        if is_sort:
            filtered_slack_messages = filtered_slack_messages[::-1]
        return filtered_slack_messages

    @classmethod
    def _get_request_messages(cls: Type[S], url, header, payload):
        response = Requests.get(url=url, headers=header, params=payload)
        messages = response.json().get("messages")
        return messages


class Requests:
    @staticmethod
    def get(**kwargs):
        return requests.get(**kwargs)

    @staticmethod
    def post(**kwargs):
        return requests.post(**kwargs)


class IFTTT:
    @staticmethod
    def post(config: Config, slack_messages: list[SlackMessage]) -> None:
        """Kick IFTTT webhook"""
        event = config.ifttt_event_name
        token = config.ifttt_webhook_token
        url = f"https://maker.ifttt.com/trigger/{event}/with/key/{token}"
        for message in slack_messages:
            payload = {"value1": message.ts, "value2": message.text}
            Requests.post(url=url, data=payload)
            print(f"message to be posted: {message.ts},{message.text}")


def read_env(path: str = ".env") -> dict[str, str]:
    """Reads the .env file and returns a dict with the values"""
    with open(path) as f:
        return {line.split("=")[0]: line.split("=")[1].strip() for line in f}


def main():
    env_dict = read_env()
    config = Config.build(env_dict)
    slack_messages = SlackMessage.get(config)
    filtered_slack_messages = SlackMessage.filter(slack_messages, datetime.today())
    IFTTT.post(config, filtered_slack_messages)


if __name__ == "__main__":
    main()
