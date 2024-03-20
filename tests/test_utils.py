import json
import os
import tempfile
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "path_exists, expected",
    [
        (
            True,
            {
                "SLACK_TOKEN": "token",
                "SLACK_CHANNEL_ID": "channel_id",
                "GOOGLE_SHEET_WORKSHEET_NAME": "worksheet_name",
                "EXCLUDE_DAYS": "1",
                "EXCLUDE_MINUTES": "2",
                "AWS_ACCOUNT_ID": "account_id",
            },
        ),
        (
            False,
            {
                "SLACK_TOKEN": "env_token",
                "SLACK_CHANNEL_ID": "env_channel_id",
                "GOOGLE_SHEET_WORKSHEET_NAME": "env_worksheet_name",
                "EXCLUDE_DAYS": "11",
                "EXCLUDE_MINUTES": "22",
                "AWS_ACCOUNT_ID": "env_account_id",
            },
        ),
    ],
)
def test_read_env(path_exists, expected, mock_env_dict):
    from kakeibo.utils import read_env

    with tempfile.TemporaryDirectory() as tempdir:
        if path_exists:
            content = ""
            for k, v in mock_env_dict.items():
                content += f"{k}={v}\n"
            with open(f"{tempdir}/.env", "w") as f:
                f.write(content)
        else:
            os.environ["SLACK_TOKEN"] = "env_token"
            os.environ["SLACK_CHANNEL_ID"] = "env_channel_id"
            os.environ["GOOGLE_SHEET_WORKSHEET_NAME"] = "env_worksheet_name"
            os.environ["EXCLUDE_DAYS"] = "11"
            os.environ["EXCLUDE_MINUTES"] = "22"
            os.environ["AWS_ACCOUNT_ID"] = "env_account_id"

        assert read_env(Path(tempdir) / (".env")) == expected


@pytest.mark.parametrize(
    "path_exists, expected",
    [
        (
            True,
            {
                "type": "type",
                "project_id": "project_id",
                "private_key_id": "private_key_id",
                "private_key": "private_key",
                "client_email": "client_email",
                "client_id": "client_id",
                "auth_uri": "auth_uri",
                "token_uri": "token_uri",
                "auth_provider_x509_cert_url": "auth_provider_x509_cert_url",
                "client_x509_cert_url": "client_x509_cert_url",
                "universe_domain": "universe_domain",
            },
        ),
        (
            False,
            {
                "type": "env_type",
                "project_id": "env_project_id",
                "private_key_id": "env_private_key_id",
                "private_key": "env_private_key",
                "client_email": "env_client_email",
                "client_id": "env_client_id",
                "auth_uri": "env_auth_uri",
                "token_uri": "env_token_uri",
                "auth_provider_x509_cert_url": "env_auth_provider_x509_cert_url",
                "client_x509_cert_url": "env_client_x509_cert_url",
                "universe_domain": "env_universe_domain",
            },
        ),
    ],
)
def test_read_client_secret(path_exists, expected, mock_google_api_client_secret):
    from kakeibo.utils import read_client_secret

    with tempfile.TemporaryDirectory() as tempdir:
        if path_exists:
            d = mock_google_api_client_secret.model_dump()
            with open(f"{tempdir}/client_secret.json", "w") as f:
                json.dump(d, f)
        else:
            os.environ["google_api_type"] = "env_type"
            os.environ["google_api_project_id"] = "env_project_id"
            os.environ["google_api_private_key_id"] = "env_private_key_id"
            os.environ["google_api_private_key"] = "env_private_key"
            os.environ["google_api_client_email"] = "env_client_email"
            os.environ["google_api_client_id"] = "env_client_id"
            os.environ["google_api_auth_uri"] = "env_auth_uri"
            os.environ["google_api_token_uri"] = "env_token_uri"
            os.environ["google_api_auth_provider_x509_cert_url"] = "env_auth_provider_x509_cert_url"
            os.environ["google_api_client_x509_cert_url"] = "env_client_x509_cert_url"
            os.environ["google_api_universe_domain"] = "env_universe_domain"

        assert read_client_secret(Path(tempdir) / "client_secret.json") == expected
