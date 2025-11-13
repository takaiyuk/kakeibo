from unittest.mock import Mock

from kakeibo.slack import SlackMessage


class TestKakeiboService:
    def _target_class(self):
        from kakeibo.service import KakeiboService

        return KakeiboService

    def _make_one(self, *args, **kwargs):
        return self._target_class()(*args, **kwargs)

    def test_get_slack_messages(self):
        mock_slack_client = Mock()
        mock_google_sheet_client = Mock()

        expected_messages = [
            SlackMessage(ts=1706788200.0, text="test1"),
            SlackMessage(ts=1706788800.0, text="test2"),
        ]
        mock_slack_client.get.return_value = expected_messages

        service = self._make_one(mock_slack_client, mock_google_sheet_client)
        result = service.get_slack_messages()

        assert result == expected_messages
        mock_slack_client.get.assert_called_once()

    def test_write_google_sheet(self):
        mock_slack_client = Mock()
        mock_google_sheet_client = Mock()

        slack_messages = [
            SlackMessage(ts=1706788200.0, text="test1"),
            SlackMessage(ts=1706788800.0, text="test2"),
        ]

        service = self._make_one(mock_slack_client, mock_google_sheet_client)
        service.write_google_sheet(slack_messages)

        mock_google_sheet_client.write.assert_called_once_with(slack_messages)
