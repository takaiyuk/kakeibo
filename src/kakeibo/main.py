import structlog

from kakeibo.config import Config, GoogleAPIClientSecret
from kakeibo.consts import EXCLUDE_DAYS, EXCLUDE_MINUTES
from kakeibo.google_sheet import GoogleSheet
from kakeibo.service import KakeiboService
from kakeibo.slack import FilterCondition, Interval, SlackAlert, SlackMessageBuilder
from kakeibo.usecase import KakeiboUseCase
from kakeibo.utils import read_client_secret, read_env


def main() -> int:
    logger = structlog.get_logger(__name__)
    env_dict = read_env()
    client_secret = read_client_secret()
    exclude_days = int(env_dict.get("EXCLUDE_DAYS", EXCLUDE_DAYS))
    exclude_minutes = int(env_dict.get("EXCLUDE_MINUTES", EXCLUDE_MINUTES))
    interval = Interval(days=exclude_days, minutes=exclude_minutes)
    filter_condition = FilterCondition(exclude_interval=interval)

    google_api_client_secret = GoogleAPIClientSecret(**client_secret)
    config = Config.build(env_dict, google_api_client_secret)
    slack_alert_client = SlackAlert(config)
    slack_client = SlackMessageBuilder(logger, config, filter_condition, slack_alert_client)
    google_sheet_client = GoogleSheet(logger, config)
    service = KakeiboService(slack_client, google_sheet_client)
    usecase = KakeiboUseCase(service)
    usecase.execute()
    return 0
