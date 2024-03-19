from datetime import datetime
from typing import Any

from kakeibo.main import IFTTT, Config, SlackMessage


def mock_config() -> Config:
    return Config.build(
        {
            "SLACK_TOKEN": "token",
            "SLACK_CHANNEL_ID": "channel_id",
            "IFTTT_WEBHOOK_TOKEN": "webhook_token",
            "IFTTT_EVENT_NAME": "event_name",
        }
    )


def mock_slack_messages(inputs: list[tuple[datetime, str]]) -> list[SlackMessage]:
    messages = [{"ts": str(datetime.timestamp(dt)), "text": text} for dt, text in inputs]
    slack_messages: list[SlackMessage] = [
        SlackMessage(ts=float(message["ts"]), text=message["text"]) for message in messages
    ]
    return slack_messages


def test_build_config() -> None:
    config = mock_config()
    assert config.slack_token == "token"
    assert config.slack_channel_id == "channel_id"
    assert config.ifttt_webhook_token == "webhook_token"
    assert config.ifttt_event_name == "event_name"


def test_get_slack_messages(mocker: Any) -> None:
    inputs = [
        (datetime(2020, 1, 1, 11, 59, 0), "included_59"),
        (datetime(2020, 1, 1, 11, 51, 0), "included_51"),
        (datetime(2020, 1, 1, 11, 49, 0), "excluded_49"),
    ]
    mock_return_value: list[dict[str, str]] = [
        {"ts": str(datetime.timestamp(input[0])), "text": input[1]} for input in inputs
    ]
    mocker.patch(
        "kakeibo.main.SlackMessage._get_request_messages",
        return_value=mock_return_value,
    )
    config = mock_config()
    slack_messages = SlackMessage.get(config)
    expected = mock_slack_messages(inputs)
    assert slack_messages == expected


def test_filter_slack_messages() -> None:
    dt_now = datetime(2020, 1, 1, 12, 0, 0)
    inputs = [
        (datetime(2020, 1, 1, 11, 59, 0), "included_59"),
        (datetime(2020, 1, 1, 11, 51, 0), "included_51"),
        (datetime(2020, 1, 1, 11, 49, 0), "excluded_49"),
    ]
    slack_messages = mock_slack_messages(inputs)
    filtered_slack_messages = SlackMessage.filter(slack_messages, dt_now)
    expected = mock_slack_messages(inputs[:-1])[::-1]
    assert filtered_slack_messages == expected


def test_post_ifttt_webhook(mocker: Any, capsys: Any) -> None:
    mocker.patch("kakeibo.main.Requests.post")
    config = mock_config()
    inputs = [
        (datetime(2020, 1, 1, 11, 59, 0), "included_59"),
        (datetime(2020, 1, 1, 11, 51, 0), "included_51"),
    ]
    slack_messages = mock_slack_messages(inputs)
    expected = "\n".join([f"message to be posted: {message.ts},{message.text}" for message in slack_messages])
    expected += "\n"
    IFTTT.post(config, slack_messages)
    output, _ = capsys.readouterr()
    assert output == expected
