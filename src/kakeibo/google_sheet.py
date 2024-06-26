import time
from typing import Any

import gspread
from gspread.utils import ValueInputOption
from gspread.worksheet import Worksheet
from oauth2client.service_account import ServiceAccountCredentials

from kakeibo.config import Config, GoogleAPIClientSecret
from kakeibo.consts import INSERT_ROWS_TEMPLATE
from kakeibo.slack import SlackMessage


class GoogleSheet:
    def __init__(self, logger: Any, config: Config) -> None:
        self.logger = logger
        self.client = self._get_client(config.google_sheet_worksheet_name, config.google_api_client_secret)

    def _get_client(self, sheet_filename: str, client_secret: GoogleAPIClientSecret) -> Worksheet:
        # use creds to create a client to interact with the Google Drive API
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(client_secret.model_dump(), scopes)
        client = gspread.authorize(creds)
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open(sheet_filename).sheet1
        return sheet

    def _create_insert_row(self, slack_message: SlackMessage) -> list[str | None]:
        row = INSERT_ROWS_TEMPLATE.copy()
        row.append(f"{slack_message.ts},{slack_message.text}")
        return row

    def write(self, slack_messages: list[SlackMessage], verbose: bool = True) -> None:
        for slack_message in slack_messages:
            row = self._create_insert_row(slack_message)
            index = len(self.client.get_all_values()) + 1
            self.client.insert_row(row, index, value_input_option=ValueInputOption.user_entered)
            if verbose:
                self.logger.info(f"Insert row: {row[-1]}")
            time.sleep(1)
