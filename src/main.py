from dataclasses import dataclass
from datetime import datetime

import requests


@dataclass
class Config:
    slack_token: str
    slack_channel_id: str
    ifttt_webhook_token: str
    ifttt_event_name: str


@dataclass
class SlackMessage:
    ts: float
    text: str


def read_env(path: str = ".env") -> dict[str, str]:
    """Reads the .env file and returns a dict with the values"""
    with open(path) as f:
        return {line.split("=")[0]: line.split("=")[1].strip() for line in f}


def build_config(env_dict: dict[str, str]) -> Config:
    return Config(
        env_dict.get("SLACK_TOKEN"),
        slack_channel_id=env_dict.get("SLACK_CHANNEL_ID"),
        ifttt_webhook_token=env_dict.get("IFTTT_WEBHOOK_TOKEN"),
        ifttt_event_name=env_dict.get("IFTTT_EVENT_NAME"),
    )


def get_slack_messages(config: Config) -> list[SlackMessage]:
    url = "https://slack.com/api/conversations.history"
    token = config.slack_token
    header = {"Authorization": f"Bearer {token}"}
    channel_id = config.slack_channel_id
    payload = {"channel": channel_id}
    response = requests.get(url, headers=header, params=payload)
    messages = response.json().get("messages")
    slack_messages = [
        SlackMessage(ts=float(message.get("ts")), text=message.get("text"))
        for message in messages
    ]
    return slack_messages


def filter_slack_messages(
    slack_messages: list[SlackMessage], exclude_days: int = 0, exclude_minutes: int = 10
) -> list[SlackMessage]:
    dt_now = datetime.today()
    filtered_slack_messages: list[SlackMessage] = []
    for message in slack_messages:
        dt_message = datetime.fromtimestamp(message.ts)
        diff_days = (dt_now - dt_message).days
        diff_minutes = (dt_now - dt_message).seconds / 60
        # 10分毎に実行されるので、10分より前のメッセージは除外する
        if diff_days > exclude_days or diff_minutes > exclude_minutes:
            break
        filtered_slack_messages.append(message)
    return filtered_slack_messages


def post_ifttt_webhook(config: Config, slack_messages: list[SlackMessage]) -> None:
    event = config.ifttt_event_name
    token = config.ifttt_webhook_token
    url = f"https://maker.ifttt.com/trigger/{event}/with/key/{token}"
    for message in slack_messages:
        payload = {"value1": message.ts, "value2": message.text}
        requests.post(url, data=payload)
        print(f"message to be posted: {message.ts},{message.text}")


def main():
    env_dict = read_env()
    config = build_config(env_dict)
    slack_messages = get_slack_messages(config)
    filtered_slack_messages = filter_slack_messages(slack_messages)
    post_ifttt_webhook(config, filtered_slack_messages)


if __name__ == "__main__":
    main()
