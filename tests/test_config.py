class Test_Config:
    def _get_target_class(self):
        from kakeibo.config import Config

        return Config

    def _make_one(self, **kwargs):
        return self._get_target_class()(**kwargs)

    def test_build(self, mock_env_dict, mock_google_api_client_secret):
        c = self._get_target_class().build(mock_env_dict, mock_google_api_client_secret)
        assert c.slack_token == "token"
        assert c.slack_channel_id == "channel_id"
        assert c.google_sheet_worksheet_name == "worksheet_name"
        assert c.google_api_client_secret == mock_google_api_client_secret
