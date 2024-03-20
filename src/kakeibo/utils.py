import json
import os
from pathlib import Path


def read_env(path: Path = Path(".env")) -> dict[str, str]:
    """Reads the .env file and returns a dict with the values"""
    if path.exists():
        with open(path) as f:
            d = {line.split("=")[0]: line.split("=")[1].strip() for line in f}
    else:
        d = {
            "SLACK_TOKEN": os.environ.get("SLACK_TOKEN", ""),
            "SLACK_CHANNEL_ID": os.environ.get("SLACK_CHANNEL_ID", ""),
            "GOOGLE_SHEET_WORKSHEET_NAME": os.environ.get("GOOGLE_SHEET_WORKSHEET_NAME", ""),
            "EXCLUDE_DAYS": os.environ.get("EXCLUDE_DAYS", ""),
            "EXCLUDE_MINUTES": os.environ.get("EXCLUDE_MINUTES", ""),
            "AWS_ACCOUNT_ID": os.environ.get("AWS_ACCOUNT_ID", ""),
        }
    return {k: v for k, v in d.items() if v != ""}


def read_client_secret(path: Path = Path("client_secret.json")) -> dict[str, str]:
    """Reads the client_secret.json file and returns a dict with the values"""
    if path.exists():
        with open(path) as f:
            d = json.load(f)
    else:
        d = {
            "type": os.environ.get("google_api_type", ""),
            "project_id": os.environ.get("google_api_project_id", ""),
            "private_key_id": os.environ.get("google_api_private_key_id", ""),
            "private_key": os.environ.get("google_api_private_key", ""),
            "client_email": os.environ.get("google_api_client_email", ""),
            "client_id": os.environ.get("google_api_client_id", ""),
            "auth_uri": os.environ.get("google_api_auth_uri", ""),
            "token_uri": os.environ.get("google_api_token_uri", ""),
            "auth_provider_x509_cert_url": os.environ.get("google_api_auth_provider_x509_cert_url", ""),
            "client_x509_cert_url": os.environ.get("google_api_client_x509_cert_url", ""),
            "universe_domain": os.environ.get("google_api_universe_domain", ""),
        }
    return {k: v for k, v in d.items() if v != ""}
