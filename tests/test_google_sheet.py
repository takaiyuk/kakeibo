class TestGoogleSheet:
    def _target(self):
        from kakeibo.google_sheet import GoogleSheet

        return GoogleSheet

    def _make_one(self, *args, **kwargs):
        return self._target()(*args, **kwargs)

    def test_write(self, mocker, mock_looger, mock_env_dict, mock_google_api_client_secret):
        from kakeibo.config import Config
        from kakeibo.slack import SlackMessage

        class MockWorksheet:
            def insert_rows(self, rows: list[list[str | None]], start_row: int, value_input_option: str) -> None:
                from kakeibo.consts import INSERT_ROWS_TEMPLATE

                template = INSERT_ROWS_TEMPLATE.copy()

                assert rows == [template + ["1706788200.0,test2"], template + ["1706788800.0,test3"]]
                assert start_row == 3
                assert value_input_option == "USER_ENTERED"

            def get_all_values(self) -> list[list[str]]:
                return [
                    ["1.0,test1"],
                    ["2.0,test2"],
                ]

        mocker.patch("kakeibo.google_sheet.GoogleSheet._get_client", return_value=MockWorksheet())
        config = Config(
            slack_token=mock_env_dict["SLACK_TOKEN"],
            slack_channel_id=mock_env_dict["SLACK_CHANNEL_ID"],
            slack_alert_channel_id=mock_env_dict["SLACK_ALERT_CHANNEL_ID"],
            google_sheet_worksheet_name=mock_env_dict["GOOGLE_SHEET_WORKSHEET_NAME"],
            google_api_client_secret=mock_google_api_client_secret,
            slack_user1=mock_env_dict["SLACK_USER1"],
            slack_user2=mock_env_dict.get("SLACK_USER2"),
        )
        google_sheet = self._make_one(mock_looger, config)
        slack_messages = [
            SlackMessage(ts=1706788200.0, text="test2", user="U123"),
            SlackMessage(ts=1706788800.0, text="test3", user="U456"),
        ]
        google_sheet.write(slack_messages, verbose=True)
