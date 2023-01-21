from bot import config
from bot import constants
from bot.database.database_funcs import DatabaseHelper
from bot.telegram_logic import handling_functions
from bot.telegram_logic.telegram_client import TelegramClient, Message, Callback, Attachment, MARKUP_TYPES
from collections.abc import Callable
from typing import Any, Optional


def add_error_to_log(text: str) -> None:
    error_log = open(constants.ERROR_LOG_NAME, "a")
    error_log.write(text + "\n\n")
    error_log.close()


class UserHandler:
    def __init__(self) -> None:
        # Dict of { telegram_id -> current user state (function on message) }
        self.__user_state: dict[int, Callable[[UserHandler, int, str, Any], tuple[Callable, Any]]] = dict()

        # Dict of { telegram_id -> user data }
        self.__user_data: dict[int, Any] = dict()

        self.__database = DatabaseHelper(constants.PATH_TO_DATABASE, constants.DATABASE_NAME)  # Main database

        self.client = TelegramClient(action_on_message=self.compute_user_message,
                                     action_on_callback=self.compute_callback)

    def is_super_admin(self, user_id: int) -> bool:
        user = self.__database.get_user_by_telegram_id(user_id)

        # Returns True if user exists and his status is SUPER_ADMIN
        return user is not None and user.status == constants.SUPER_ADMIN_STATUS

    def is_admin(self, user_id: int) -> bool:
        user = self.__database.get_user_by_telegram_id(user_id)

        # Returns True if user exists and his status is ADMIN or SUPER_ADMIN
        return user is not None and (
                    user.status == constants.ADMIN_STATUS or user.status == constants.SUPER_ADMIN_STATUS)

    def is_student(self, user_id: int) -> bool:
        user = self.__database.get_user_by_telegram_id(user_id)

        # Returns True if user exists and his status is STUDENT
        return user is not None and user.status == constants.STUDENT_STATUS

    def send_message(self, send_id: int, text: str, attachments: Optional[list[Attachment]] = None,
                     markup: MARKUP_TYPES = None) -> None:
        self.client.send_message(send_id=send_id, text=text, attachments=attachments, markup=markup)

    def add_user(self, user_id: int) -> None:
        # Add new user state, if user is not exists

        if user_id not in self.__user_state:
            self.__user_state[user_id] = handling_functions.default_state
            self.__user_data[user_id] = None

    def compute_callback(self, callback: Callback) -> None:
        self.add_user(callback.from_id)

    def compute_user_message(self, message: Message) -> None:
        self.add_user(message.from_id)
        self.__user_state[message.from_id], self.__user_data[message.from_id] = \
            self.__user_state[message.from_id](self, message.from_id, message.text, self.__user_data[message.from_id])

    def run(self) -> None:
        # This function launch bot

        self.client.run(config.TELEGRAM_TOKEN)
