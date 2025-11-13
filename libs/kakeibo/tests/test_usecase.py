from unittest.mock import Mock

from kakeibo.slack import SlackMessage


class TestKakeiboUseCase:
    def _target_class(self):
        from kakeibo.usecase import KakeiboUseCase

        return KakeiboUseCase

    def _make_one(self, *args, **kwargs):
        return self._target_class()(*args, **kwargs)

    def test_execute(self):
        mock_kakeibo_service = Mock()

        expected_messages = [
            SlackMessage(ts=1706788200.0, text="test1"),
            SlackMessage(ts=1706788800.0, text="test2"),
        ]
        mock_kakeibo_service.get_slack_messages.return_value = expected_messages

        usecase = self._make_one(mock_kakeibo_service)
        usecase.execute()

        mock_kakeibo_service.get_slack_messages.assert_called_once()
        mock_kakeibo_service.write_google_sheet.assert_called_once_with(expected_messages)
