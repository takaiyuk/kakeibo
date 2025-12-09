import pytest
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


class TestSlackMessage:
    def _target_class(self):
        from kakeibo.slack import SlackMessage

        return SlackMessage

    def _make_one(self, *args, **kwargs):
        return self._target_class()(*args, **kwargs)

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("Line1\nLine2\nLine3", True),
            ("NoNewlineHere", False),
        ],
    )
    def test_has_newline(self, text, expected):
        message = self._make_one(ts=1.0, text=text, user="U123")
        assert message.has_newline() is expected


class TestSlackMessages:
    def _target_class(self):
        from kakeibo.slack import SlackMessages

        return SlackMessages

    def test_build(self):
        from kakeibo.slack import SlackMessage

        slack_messages = self._target_class().build(
            [
                {"ts": "1.0", "text": "test1", "user": "U123"},
                {"ts": "2.0", "text": "test2", "user": "U456"},
            ]
        )
        expected = [
            SlackMessage(ts=1.0, text="test1", user="U123"),
            SlackMessage(ts=2.0, text="test2", user="U456"),
        ]
        assert slack_messages.slack_messages == expected

    @freeze_time("2024-02-01 12:00:00")
    def test_filter(self):
        from kakeibo.slack import Interval, SlackMessage

        slack_messages = self._target_class().build(
            [
                {"ts": "1706788800.0", "text": "test4", "user": "U456"},  # 2024-02-01 12:00:00 JST
                {"ts": "1706788260.0", "text": "[ignore] test3", "user": "U123"},  # 2024-02-01 11:51:00 JST
                {"ts": "1706788200.0", "text": "test2", "user": "U123"},  # 2024-02-01 11:50:00 JST
                {"ts": "1706788140.0", "text": "test1", "user": "U456"},  # 2024-02-01 11:49:00 JST
            ]
        )
        slack_messages.filter(exclude_interval=Interval(days=0, minutes=10))
        expected = [
            SlackMessage(ts=1706788800.0, text="test4", user="U456"),
            SlackMessage(ts=1706788200.0, text="test2", user="U123"),
        ]
        assert slack_messages.slack_messages == expected


class TestSlack:
    def _target_class(self):
        from kakeibo.slack import SlackMessageBuilder

        return SlackMessageBuilder

    def _make_one(self, *args, **kwargs):
        return self._target_class()(*args, **kwargs)

    @freeze_time("2024-02-01 12:00:00")
    def test_get(self, mocker, mock_looger, mock_env_dict, mock_google_api_client_secret):
        from kakeibo.config import Config
        from kakeibo.slack import FilterCondition, Interval, SlackMessage

        class MockResponse:
            def json(self):
                return {
                    "messages": [
                        {"ts": "1706788260.0", "text": "test3", "user": "U123"},
                        {"ts": "1706788200.0", "text": "test2", "user": "U456"},
                        {"ts": "1706788140.0", "text": "test1", "user": "U789"},
                    ]
                }

        class MockResponseWithNewline:
            def json(self):
                return {
                    "messages": [
                        {"ts": "1706788260.0", "text": "test3,300", "user": "U123"},
                        {"ts": "1706788140.0", "text": "test1,100,2\ntest2,200", "user": "U789"},
                    ]
                }

        config = Config(
            slack_token=mock_env_dict["SLACK_TOKEN"],
            slack_channel_id=mock_env_dict["SLACK_CHANNEL_ID"],
            google_sheet_worksheet_name=mock_env_dict["GOOGLE_SHEET_WORKSHEET_NAME"],
            google_api_client_secret=mock_google_api_client_secret,
            slack_user1=mock_env_dict["SLACK_USER1"],
            slack_user2=mock_env_dict.get("SLACK_USER2"),
        )

        filter_condition = FilterCondition()
        slack = self._make_one(mock_looger, config, filter_condition)
        mocker.patch("requests.get", return_value=MockResponse())
        slack_messages = slack.build()
        expected = [
            SlackMessage(ts=1706788140.0, text="test1", user="U789"),
            SlackMessage(ts=1706788200.0, text="test2", user="U456"),
            SlackMessage(ts=1706788260.0, text="test3", user="U123"),
        ]
        assert slack_messages == expected

        filter_condition = FilterCondition(exclude_interval=Interval(days=0, minutes=10))
        slack = self._make_one(mock_looger, config, filter_condition)
        mocker.patch("requests.get", return_value=MockResponse())
        slack_messages = slack.build()
        expected = [
            SlackMessage(ts=1706788200.0, text="test2", user="U456"),
            SlackMessage(ts=1706788260.0, text="test3", user="U123"),
        ]
        assert slack_messages == expected

        filter_condition = FilterCondition()
        slack = self._make_one(mock_looger, config, filter_condition)
        mocker.patch("requests.get", return_value=MockResponseWithNewline())
        slack_messages = slack.build()
        expected = [
            SlackMessage(ts=1706788140.0, text="test1,100,2", user="U789"),
            SlackMessage(ts=1706788140.0, text="test2,200", user="U789"),
            SlackMessage(ts=1706788260.0, text="test3,300,1", user="U123"),
        ]
        for actual, expect in zip(slack_messages, expected, strict=False):
            assert actual.ts == pytest.approx(expect.ts, 1e-6)  # tsに微小な差分をつけているため近似比較
            assert actual.text == expect.text
            assert actual.user == expect.user
