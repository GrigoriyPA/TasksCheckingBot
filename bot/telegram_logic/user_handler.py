from bot import config
from bot import constants
from bot.database.database_funcs import DatabaseHelper
from bot.telegram_logic import handling_functions
from bot.telegram_logic.telegram_client import TelegramClient, Message, Callback
from collections.abc import Callable
from typing import Any


def add_error_to_log(text: str) -> None:
    error_log = open(constants.ERROR_LOG_NAME, "a")
    error_log.write(text + "\n\n")
    error_log.close()


class UserHandler:
    def __init__(self) -> None:
        # Dict of { telegram_id -> current user state (function on message) }
        self.__user_state: dict[int, Callable[[UserHandler, int, str], tuple[Any, Any]]] = dict()

        # Dict of { telegram_id -> user data }
        self.__user_data: dict[int, Any] = dict()

        self.__database = DatabaseHelper(constants.PATH_TO_DATABASE, constants.DATABASE_NAME)  # Main database

        self.client = TelegramClient(action_on_message=self.compute_user_message,
                                     action_on_callback=self.compute_callback)

    def add_user(self, user_id: int) -> None:
        # Add new user state, if user is not exists

        if user_id not in self.__user_state:
            self.__user_state[user_id] = handling_functions.default_state
            self.__user_data[user_id] = None

    def compute_callback(self, callback: Callback) -> None:
        self.add_user(callback.from_id)

    def compute_user_message(self, message: Message) -> None:
        self.add_user(message.from_id)
        self.__user_state[message.from_id](self, message.from_id, message.text)

    def run(self) -> None:
        # This function launch bot

        self.client.run(config.TELEGRAM_TOKEN)
