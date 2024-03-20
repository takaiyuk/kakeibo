from typing import Any

from kakeibo.main import main


def lambda_handler(event: Any, context: Any) -> None:
    main()
