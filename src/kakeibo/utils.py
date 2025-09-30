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
        if "type" not in d:
            d["type"] = d.pop("google_api_type", "")
        if "project_id" not in d:
            d["project_id"] = d.pop("google_api_project_id", "")
        if "private_key_id" not in d:
            d["private_key_id"] = d.pop("google_api_private_key_id", "")
        if "private_key" not in d:
            d["private_key"] = d.pop("google_api_private_key", "")
        if "client_email" not in d:
            d["client_email"] = d.pop("google_api_client_email", "")
        if "client_id" not in d:
            d["client_id"] = d.pop("google_api_client_id", "")
        if "auth_uri" not in d:
            d["auth_uri"] = d.pop("google_api_auth_uri", "")
        if "token_uri" not in d:
            d["token_uri"] = d.pop("google_api_token_uri", "")
        if "auth_provider_x509_cert_url" not in d:
            d["auth_provider_x509_cert_url"] = d.pop("google_api_auth_provider_x509_cert_url", "")
        if "client_x509_cert_url" not in d:
            d["client_x509_cert_url"] = d.pop("google_api_client_x509_cert_url", "")
        if "universe_domain" not in d:
            d["universe_domain"] = d.pop("google_api_universe_domain", "")
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
