from datetime import datetime
from typing import Any

from src.main import IFTTT, Config, SlackMessage


def mock_config():
    return Config.build(
        {
            "SLACK_TOKEN": "token",
            "SLACK_CHANNEL_ID": "channel_id",
            "IFTTT_WEBHOOK_TOKEN": "webhook_token",
            "IFTTT_EVENT_NAME": "event_name",
        }
    )


def test_build_config():
    config = mock_config()
    assert config.slack_token == "token"
    assert config.slack_channel_id == "channel_id"
    assert config.ifttt_webhook_token == "webhook_token"
    assert config.ifttt_event_name == "event_name"


def test_get_slack_messages(mocker):
    mock_return_value: list[dict[str, Any]] = [
        {"ts": ts, "text": text} for ts, text in ((1.1, "a"), (2.2, "b"), (3.3, "c"))
    ]
    expected: list[SlackMessage] = [
        SlackMessage(ts=float(message.get("ts")), text=message.get("text"))
        for message in mock_return_value
    ]
    mocker.patch(
        "src.main.SlackMessage._get_request_messages", return_value=mock_return_value
    )
    config = mock_config()
    slack_messages = SlackMessage.get(config)
    assert slack_messages == expected


def test_filter_slack_messages():
    dt_now = datetime(2020, 1, 1, 12, 0, 0)
    inputs = [
        (datetime(2020, 1, 1, 11, 59, 0), "included_59"),
        (datetime(2020, 1, 1, 11, 51, 0), "included_51"),
        (datetime(2020, 1, 1, 11, 49, 0), "excluded_49"),
    ]
    messages = [{"ts": datetime.timestamp(dt), "text": text} for dt, text in inputs]
    slack_messages: list[SlackMessage] = [
        SlackMessage(ts=float(message.get("ts")), text=message.get("text"))
        for message in messages
    ]
    expected: list[SlackMessage] = [
        SlackMessage(ts=float(message.get("ts")), text=message.get("text"))
        for message in messages[:-1]
    ][::-1]
    filtered_slack_messages = SlackMessage.filter(slack_messages, dt_now)
    assert filtered_slack_messages == expected


def test_post_ifttt_webhook(mocker, capsys):
    mocker.patch("src.main.Requests.post")
    config = mock_config()
    inputs = [
        (datetime(2020, 1, 1, 11, 59, 0), "included_59"),
        (datetime(2020, 1, 1, 11, 51, 0), "included_51"),
    ]
    messages = [{"ts": datetime.timestamp(dt), "text": text} for dt, text in inputs]
    slack_messages: list[SlackMessage] = [
        SlackMessage(ts=float(message.get("ts")), text=message.get("text"))
        for message in messages
    ]
    expected = [
        f"message to be posted: {message.ts},{message.text}"
        for message in slack_messages
    ]
    expected = "\n".join(expected)
    expected += "\n"
    IFTTT.post(config, slack_messages)
    out, _ = capsys.readouterr()
    assert out == expected
