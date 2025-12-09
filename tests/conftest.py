from typing import Any

from pytest import fixture

from kakeibo.config import GoogleAPIClientSecret
from kakeibo.slack import SlackMessage


@fixture
def mock_looger() -> Any:
    class MockLogger:
        def debug(self, message: str) -> None:
            pass

        def info(self, message: str) -> None:
            pass

        def warning(self, message: str) -> None:
            pass

    return MockLogger()


@fixture
def mock_env_dict() -> dict[str, str]:
    return {
        "SLACK_TOKEN": "token",
        "SLACK_CHANNEL_ID": "channel_id",
        "SLACK_ALERT_CHANNEL_ID": "alert_channel_id",
        "GOOGLE_SHEET_WORKSHEET_NAME": "worksheet_name",
        "EXCLUDE_DAYS": "1",
        "EXCLUDE_MINUTES": "2",
        "AWS_ACCOUNT_ID": "account_id",
        "SLACK_USER1": "U123",
        "SLACK_USER2": "",
    }


@fixture
def mock_google_api_client_secret() -> GoogleAPIClientSecret:
    return GoogleAPIClientSecret(
        type="type",
        project_id="project_id",
        private_key_id="private_key_id",
        private_key="private_key",
        client_email="client_email",
        client_id="client_id",
        auth_uri="auth_uri",
        token_uri="token_uri",
        auth_provider_x509_cert_url="auth_provider_x509_cert_url",
        client_x509_cert_url="client_x509_cert_url",
        universe_domain="universe_domain",
    )


@fixture
def mock_slack_messages() -> list[SlackMessage]:
    return [
        SlackMessage(ts=1706788200.0, text="test1", user="U123"),
        SlackMessage(ts=1706788800.0, text="test2", user="U456"),
    ]
