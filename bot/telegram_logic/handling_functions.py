from bot.telegram_logic.user_handler import UserHandler
from typing import Any


def default_state(handler: UserHandler, from_id: int, text: str) -> tuple[Any, Any]:
    print(text)
    return 0, 0
