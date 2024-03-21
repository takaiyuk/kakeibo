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
            def insert_row(self, row: list[str | None], index: int, value_input_option: str) -> None:
                from kakeibo.consts import INSERT_ROWS_TEMPLATE

                template = INSERT_ROWS_TEMPLATE.copy()

                assert row == template + ["1706788200.0,test2"] or row == template + ["1706788800.0,test3"]
                assert index == 3
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
            google_sheet_worksheet_name=mock_env_dict["GOOGLE_SHEET_WORKSHEET_NAME"],
            google_api_client_secret=mock_google_api_client_secret,
        )
        google_sheet = self._make_one(mock_looger, config)
        slack_messages = [
            SlackMessage(ts=1706788200.0, text="test2"),
            SlackMessage(ts=1706788800.0, text="test3"),
        ]
        google_sheet.write(slack_messages, verbose=True)
