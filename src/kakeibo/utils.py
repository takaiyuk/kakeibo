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
                if key == "private_key":
                    d[key] = modify_private_key(d.pop(f"google_api_{key}", ""))
                else:
                    d[key] = d.pop(f"google_api_{key}", "")
    else:
        d = {k: os.environ.get(f"google_api_{k}", "") for k in GOOGLE_API_KEYS}
    return {k: v for k, v in d.items() if v != ""}


def modify_private_key(key: str) -> str:
    """
    Modifies the private key by replacing the escaped newlines with actual newlines.

    from `-----BEGIN PRIVATE KEY----- xxxx yyyy zzzz  -----END PRIVATE KEY-----`
    to `-----BEGIN PRIVATE KEY-----\nxxxx\nyyyy\nzzzz\n-----END PRIVATE KEY-----`
    """
    # If the key doesn't have newlines but has spaces between the header/footer and content
    if "\n" not in key and "-----BEGIN PRIVATE KEY-----" in key and "-----END PRIVATE KEY-----" in key:
        # Extract the parts
        parts = key.split("-----BEGIN PRIVATE KEY-----")
        if len(parts) == 2:
            remaining = parts[1].split("-----END PRIVATE KEY-----")
            if len(remaining) == 2:
                content = remaining[0].strip()
                content = content.replace(" ", "")  # Replace spaces with nothing
                # Split content by spaces and rejoin with newlines
                # Each line in a PEM private key is typically 64 characters
                lines = []
                for i in range(0, len(content), 64):
                    lines.append(content[i : i + 64].strip())
                # Reconstruct the key with proper formatting
                key = f"-----BEGIN PRIVATE KEY-----\n{'\n'.join(lines)}\n-----END PRIVATE KEY-----"
    return key
