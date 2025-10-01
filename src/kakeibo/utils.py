import json
import os
from pathlib import Path

from kakeibo.config import GOOGLE_API_KEYS


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
        for key in GOOGLE_API_KEYS:
            if key not in d:
                d[key] = d.pop(f"google_api_{key}", "")
    else:
        d = {k: os.environ.get(f"google_api_{k}", "") for k in GOOGLE_API_KEYS}
    return {k: v for k, v in d.items() if v != ""}
