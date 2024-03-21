from freezegun import freeze_time


class TestInterval:
    def _target_class(self):
        from kakeibo.slack import Interval

        return Interval

    def _make_one(self, *args, **kwargs):
        return self._target_class()(*args, **kwargs)

    def test_convert_minutes(self):
        interval = self._make_one(days=1, minutes=10)
        assert interval.convert_minutes() == 1450


class TestSlackMessages:
    def _target_class(self):
        from kakeibo.slack import SlackMessages

        return SlackMessages

    def _make_one(self, *args, **kwargs):
        return self._target_class()(*args, **kwargs)

    def test_build(self):
        from kakeibo.slack import SlackMessage

        slack_messages = self._target_class().build(
            [
                {"ts": "1.0", "text": "test1"},
                {"ts": "2.0", "text": "test2"},
            ]
        )
        expected = [
            SlackMessage(ts=1.0, text="test1"),
            SlackMessage(ts=2.0, text="test2"),
        ]
        assert slack_messages.slack_messages == expected

    @freeze_time("2024-02-01 12:00:00")
    def test_filter(self):
        from kakeibo.slack import Interval, SlackMessage

        slack_messages = self._target_class().build(
            [
                {"ts": "1706788800.0", "text": "test3"},  # 2024-02-01 12:00:00 JST
                {"ts": "1706788200.0", "text": "test2"},  # 2024-02-01 11:50:00 JST
                {"ts": "1706788140.0", "text": "test1"},  # 2024-02-01 11:49:00 JST
            ]
        )
        slack_messages.filter(
            exclude_interval=Interval(days=0, minutes=10),
            is_sort=True,
        )
        expected = [
            SlackMessage(ts=1706788200.0, text="test2"),
            SlackMessage(ts=1706788800.0, text="test3"),
        ]
        assert slack_messages.slack_messages == expected


class TestSlack:
    def _target_class(self):
        from kakeibo.slack import Slack

        return Slack

    def _make_one(self, *args, **kwargs):
        return self._target_class()(*args, **kwargs)

    def test_get(self, mocker, mock_env_dict, mock_google_api_client_secret):
        from kakeibo.config import Config
        from kakeibo.slack import FilterCondition, SlackMessage

        class MockResponse:
            def json(self):
                return {"messages": [{"ts": "1706788800.0", "text": "test3"}]}

        config = Config(
            slack_token=mock_env_dict["SLACK_TOKEN"],
            slack_channel_id=mock_env_dict["SLACK_CHANNEL_ID"],
            google_sheet_worksheet_name=mock_env_dict["GOOGLE_SHEET_WORKSHEET_NAME"],
            google_api_client_secret=mock_google_api_client_secret,
        )
        filter_condition = FilterCondition()
        slack = self._make_one(config, filter_condition)
        mocker.patch("requests.get", return_value=MockResponse())
        slack_messages = slack.get()
        expected = [SlackMessage(ts=1706788800.0, text="test3")]
        assert slack_messages == expected
