from bot import config
from bot import constants
from bot.database.database_funcs import DatabaseHelper
from bot.telegram_logic import handling_functions
from bot.telegram_logic.telegram_client import TelegramClient, Message, Callback, Attachment, MARKUP_TYPES
from bot.user import User
from bot.homework import Homework
from collections.abc import Callable
from typing import Any, Optional


def add_error_to_log(text: str) -> None:
    error_log = open(constants.ERROR_LOG_PATH + constants.ERROR_LOG_NAME, "a")
    error_log.write(text + "\n\n")
    error_log.close()


class UserHandler:
    def __init__(self) -> None:
        # Dict of { telegram_id -> current user state (function on message) }
        self.__user_state: dict[int, Callable[[UserHandler, int, str, Any], tuple[Callable, Any]]] = dict()

        # Dict of { telegram_id -> user data }
        self.__user_data: dict[int, Any] = dict()

        self.__database = DatabaseHelper(constants.PATH_TO_DATABASE, constants.DATABASE_NAME)  # Main database

        self.client = TelegramClient(action_on_message=self.__compute_user_message,
                                     action_on_callback=self.__compute_callback)

    # Access to user statistic
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

    def is_exists_login(self, login: str) -> bool:
        return self.__database.get_user_by_login(login) is not None

    def is_valid_password(self, login: str, password: str) -> bool:
        user = self.__database.get_user_by_login(login)
        return user is not None and user.password == password

    def get_user_info_by_login(self, login: str) -> Optional[User]:
        return self.__database.get_user_by_login(login)

    def get_user_info_by_id(self, user_id: id) -> Optional[User]:
        return self.__database.get_user_by_telegram_id(user_id)

    # Access to exercise statistic
    def is_exists_exercise_name(self, exercise_name: str) -> bool:
        return self.__database.get_homework_by_name(exercise_name) is not None

    def get_all_exercises_names(self) -> list[str]:
        return self.__database.get_all_homeworks_names()

    def get_all_exercises_names_for_grade(self, grade: int) -> list[str]:
        return self.__database.get_all_homeworks_names_for_grade(grade)

    def get_exercise_info_by_name(self, exercise_name: str) -> Optional[Homework]:
        return self.__database.get_homework_by_name(exercise_name)

    # Change user data
    def sign_in_user(self, login: str, user_id: int) -> None:
        self.__database.change_user_telegram_id(login, user_id)

    def sign_out_user(self, user_id: int) -> None:
        user = self.__database.get_user_by_telegram_id(user_id)
        if user is not None:
            self.__database.change_user_telegram_id(user.login, constants.UNAUTHORIZED_TELEGRAM_ID)

    def delete_user(self, login: str) -> None:
        self.__database.delete_user_by_login(login)

    def update_user_state(self, user_id: int, new_state: Callable[[Any, int, str, Any], tuple[Callable, Any]],
                          new_data) -> None:
        self.__user_state[user_id] = new_state
        self.__user_data[user_id] = new_data

    # Change exercise data
    def delete_exercise(self, exercise_name: str) -> None:
        self.__database.delete_homework_by_name(exercise_name)

    # Bot interface
    def __add_user(self, user_id: int) -> None:
        # Add new user state, if user is not exists

        if user_id not in self.__user_state:
            self.__user_state[user_id] = handling_functions.default_state
            self.__user_data[user_id] = None

    def __compute_callback(self, callback: Callback) -> None:
        # Skip all callbacks from chats
        if callback.is_from_chat():
            return

        self.__add_user(callback.from_id)

    def __compute_user_message(self, message: Message) -> None:
        # Skip all messages from chats
        if message.is_from_chat():
            return

        self.__add_user(message.from_id)
        self.__user_state[message.from_id], self.__user_data[message.from_id] = \
            self.__user_state[message.from_id](self, message.from_id, message.text, self.__user_data[message.from_id])

    def send_message(self, send_id: int, text: str, attachments: Optional[list[Attachment]] = None,
                     markup: MARKUP_TYPES = None) -> None:
        try:
            self.client.send_message(send_id=send_id, text=text, attachments=attachments, markup=markup)
        except Exception as error:
            add_error_to_log("Unknown error while sending the message.\nDescription:\n" + str(error))

    def run(self) -> None:
        # This function launch bot

        self.client.run(config.TELEGRAM_TOKEN)
