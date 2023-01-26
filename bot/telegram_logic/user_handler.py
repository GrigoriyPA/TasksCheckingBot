from bot import config, constants
from bot.database.database_funcs import DatabaseHelper
from bot.entities.homework import Homework
from bot.entities.task import Task
from bot.entities.user import User
from bot.telegram_logic import handling_functions, callback_functions
from bot.telegram_logic.interface import messages_text
from bot.telegram_logic.client.telegram_client import TelegramClient, Message, Callback, Attachment, MARKUP_TYPES
from collections.abc import Callable
from telebot import types
from typing import Any, Optional


def add_error_to_log(text: str) -> None:
    error_log = open(constants.ERROR_LOG_PATH + constants.ERROR_LOG_NAME, "a")
    error_log.write(text + "\n\n")
    error_log.close()


def check_new_name(login: str) -> bool:
    # Check login, returns True if all ASCII codes are good

    for symbol in login:
        if ord(symbol) > constants.MAXIMUM_ASCII_CODE_IN_NAMES:
            return False
    return True


class UserHandler:
    def __init__(self) -> None:
        # Dict of { telegram_id -> current user state (function on message) }
        self.__user_state: dict[int, Callable[[UserHandler, int, str, Any], tuple[Callable, Any]]] = dict()

        # Dict of { telegram_id -> user data }
        self.__user_data: dict[int, Any] = dict()

        # Dict of { telegram_id -> attachment in last message }
        self.current_user_attachment: dict[int, Optional[Attachment]] = dict()

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

    def is_authorized(self, user_id: int) -> bool:
        return self.__database.get_user_by_telegram_id(user_id) is not None

    def is_exists_login(self, login: str) -> bool:
        return self.__database.get_user_by_login(login) is not None

    def is_valid_password(self, login: str, password: str) -> bool:
        user = self.__database.get_user_by_login(login)
        return user is not None and user.password == password

    def get_user_info_by_login(self, login: str) -> Optional[User]:
        return self.__database.get_user_by_login(login)

    def get_user_info_by_id(self, user_id: id) -> Optional[User]:
        return self.__database.get_user_by_telegram_id(user_id)

    def get_users_info_by_status(self, status: str) -> list[User]:
        return self.__database.get_all_users_with_status(status)

    # Access to exercise statistic
    def is_exists_exercise_name(self, exercise_name: str) -> bool:
        return self.__database.get_homework_by_name(exercise_name) is not None

    def get_all_exercises_names(self) -> list[str]:
        homeworks_names = []
        for homework in self.__database.get_all_homeworks():
            homeworks_names.append(homework.name)
        return homeworks_names

    def get_all_exercises_names_for_grade(self, grade: int) -> list[str]:
        homeworks_names = []
        for homework in self.__database.get_all_homeworks_for_grade(grade):
            homeworks_names.append(homework.name)
        return homeworks_names

    def get_results_of_students_by_exercise_name(self, exercise_name: str) -> Optional[
        list[tuple[User, list[tuple[str, str]]]]]:
        return self.__database.get_results(constants.STUDENT_STATUS, exercise_name)

    def get_exercise_info_by_name(self, exercise_name: str) -> Optional[Homework]:
        return self.__database.get_homework_by_name(exercise_name)

    def get_number_of_right_answers_on_task(self, login: str, exercise_name: str) -> int:
        exercise_info = self.__database.get_homework_by_name(exercise_name)
        tasks_number = len(exercise_info.tasks)
        solved_tasks_number = 0
        for i in range(1, tasks_number + 1):
            solved_tasks_number += self.__database.get_user_answer_for_the_task(login, exercise_name, i) in \
                                   exercise_info.tasks[i - 1].right_answers
        return solved_tasks_number

    def get_user_answer_on_task(self, login: str, exercise_name: str, task_id: int) -> Optional[str]:
        return self.__database.get_user_answer_for_the_task(login, exercise_name, task_id)

    def get_right_answer_on_task(self, exercise_name: str, task_id: int) -> list[str]:
        return self.__database.get_right_answers_for_the_task(exercise_name, task_id)

    def check_task(self, login: str, homework_name: str, task_id: int) -> Optional[bool]:
        user = self.__database.get_user_by_login(login)

        # If there is no such user just return None
        if user is None:
            return None

        user_answer = self.__database.get_user_answer_for_the_task(login, homework_name, task_id)

        # If user did not give any answers just return None
        if user_answer is None:
            return None

        # Returns True if user answer is right
        return user_answer.text_answer in self.__database.get_right_answers_for_the_task(homework_name, task_id)

    def get_user_results_on_exercises(self, login: str, exercises_names: list[str]) -> list[tuple[int, int]]:
        user_results: list[tuple[int, int]] = []  # List of pairs (solved tasks number, tasks number)
        for exercise_name in exercises_names:
            exercise_info = self.__database.get_homework_by_name(exercise_name)
            tasks_number = len(exercise_info.tasks)

            # Calculate solved tasks number in current homework
            solved_tasks_number = 0
            for i in range(1, tasks_number + 1):
                solved_tasks_number += self.__database.get_user_answer_for_the_task(login, exercise_name, i) in \
                                       exercise_info.tasks[i - 1].right_answers

            user_results.append((solved_tasks_number, tasks_number))
        return user_results

    # Change user data
    def sign_in_user(self, login: str, user_id: int) -> None:
        self.__database.change_user_telegram_id(login, user_id)

    def sign_out_user(self, user_id: int) -> None:
        user = self.__database.get_user_by_telegram_id(user_id)
        if user is not None:
            self.__database.change_user_telegram_id(user.login, constants.UNAUTHORIZED_TELEGRAM_ID)

    def add_user(self, login: str, password: str, status: str, grade: int = -1) -> None:
        self.__database.add_user(User(login=login, password=password, status=status,
                                      telegram_id=constants.UNAUTHORIZED_TELEGRAM_ID, grade=grade))

    def delete_user(self, login: str) -> None:
        self.__database.delete_user_by_login(login)

    def update_user_state(self, user_id: int, new_state: Callable[[Any, int, str, Any], tuple[Callable, Any]],
                          new_data) -> None:
        self.__user_state[user_id] = new_state
        self.__user_data[user_id] = new_data

    # Change exercise data
    def add_exercise(self, data) -> None:
        tasks = []
        for i in range(1, data["number_tasks"] + 1):
            if i in data["task_statements"]:
                tasks.append(
                    Task(homework_id=-1, task_number=i, right_answers=data["right_answers"][i],
                         text_statement=data["task_statements"][i]["text_statement"],
                         file_statement=(data["task_statements"][i]["statement_data"],
                                         data["task_statements"][i]["statement_ext"])))
            else:
                tasks.append(
                    Task(homework_id=-1, task_number=i, right_answers=data["right_answers"][i],
                         text_statement='',
                         file_statement=(bytes(), '')))
        self.__database.add_homework(Homework(data["exercise_name"], data["exercise_grade"], tasks))

    def delete_exercise(self, exercise_name: str) -> None:
        self.__database.delete_homework_by_name(exercise_name)

    def send_answer_on_exercise(self, login: str, exercise_name: str, task_id: int, answer: str) -> Optional[str]:
        return self.__database.send_answer_for_the_task(login, exercise_name, task_id, answer, (bytes(), ''))

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
        new_state, new_data = \
            callback_functions.compute_callback(self, callback.from_id, callback.message_id, callback.text,
                                                callback.callback_data)

        if new_state is not None:
            self.__user_state[callback.from_id], self.__user_data[callback.from_id] = new_state, new_data

    def __compute_user_message(self, message: Message) -> None:
        # Skip all messages from chats
        if message.is_from_chat():
            return

        if message.from_id in self.__user_state and message.text == "/start":
            self.send_message(send_id=message.from_id, text=messages_text.MESSAGE_ON_START_COMMAND)
            handling_functions.default_state(self, message.from_id, message.text, self.__user_data[message.from_id])
            return

        self.current_user_attachment[message.from_id] = message.attachment

        self.__add_user(message.from_id)
        self.__user_state[message.from_id], self.__user_data[message.from_id] = \
            self.__user_state[message.from_id](self, message.from_id, message.text, self.__user_data[message.from_id])

        self.current_user_attachment[message.from_id] = None

    def edit_message(self, from_id: int, message_id: int, text: str, markup: MARKUP_TYPES = None) -> bool:
        try:
            self.client.edit_message(from_id=from_id, message_id=message_id, text=text, markup=markup)
            return True
        except Exception as error:
            return False

    def send_message(self, send_id: int, text: str, attachments: Optional[list[Attachment]] = None,
                     markup: MARKUP_TYPES = None) -> None:
        try:
            self.client.send_message(send_id=send_id, text=text, attachments=attachments, markup=markup)
        except Exception as error:
            add_error_to_log("Unknown error while sending the message.\nDescription:\n" + str(error))

    def get_chat_member(self, chat_id: int, user_id: int) -> types.ChatMember:
        return self.client.get_chat_member(chat_id=chat_id, user_id=user_id)

    def run(self) -> None:
        # This function launch bot

        self.client.run(config.TELEGRAM_TOKEN)
