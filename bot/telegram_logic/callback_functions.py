from bot.telegram_logic import inline_markups
from collections.abc import Callable
from typing import Any, Optional

# common
MESSAGE_ON_UNAUTHORIZED_USER = "Вы не авторизованы."
MESSAGE_ON_UNKNOWN_EXERCISE_NAME = "Выбранное задание недоступно."

# compute_show_results_table_callback
MESSAGE_ON_SUCCESS_CREATION_TABLE = "Текущие результаты по работе '{exercise_name}', {grade} класс:"

# compute_show_login_in_results_table_callback
MESSAGE_ON_SHOW_LOGIN_IN_RESULTS_TABLE = "{login}\nРешено {solved_tasks_number} / {tasks_number} задач."


def compute_callback(handler, from_id: int, message_id: int, callback_data: str) -> tuple[Optional[Callable], Any]:
    # Parsing callback data
    callback_type = callback_data[0]
    callback_data = callback_data[1:].split(inline_markups.CALLBACK_SEPARATION_ELEMENT)

    return CALLBACK_HANDLING_FUNCTION[callback_type](handler, from_id, message_id, callback_data)


# Callback computing functions

def compute_none_callback(handler, from_id: int, message_id: int,
                          callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # Do nothing
    return None, None


def compute_show_results_table_callback(handler, from_id: int, message_id: int,
                                        callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user chooses homework for show results (in list of homeworks)

    # If user is not authorized, reject choice
    if not handler.is_authorized(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNAUTHORIZED_USER)
        return None, None

    exercise_name = callback_data[0]  # Getting stored exercise name
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Creating table of results
    markup = inline_markups.get_results_table_inline_markup(
        handler.get_results_of_students_by_exercise_name(exercise_name), exercise_name,
        len(exercise_info.right_answers), 1)

    # Sending table
    handler.send_message(send_id=from_id,
                         text=MESSAGE_ON_SUCCESS_CREATION_TABLE.format(exercise_name=exercise_name,
                                                                       grade=str(exercise_info.grade)),
                         markup=markup)
    return None, None


def compute_show_login_in_results_table_callback(handler, from_id: int, message_id: int,
                                                 callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user wants to see statistic of one user in results table

    # If user is not authorized, reject choice
    if not handler.is_authorized(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNAUTHORIZED_USER)
        return None, None

    login, exercise_name = callback_data[0], callback_data[1]  # Getting chooses login and exercise name
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Calculation number of right solved tasks
    tasks_number = len(exercise_info.right_answers)
    solved_tasks_number = handler.get_number_of_right_answers_on_task(login, exercise_name)

    # Send statistic
    handler.send_message(send_id=from_id,
                         text=MESSAGE_ON_SHOW_LOGIN_IN_RESULTS_TABLE.format(login=login,
                                                                            solved_tasks_number=str(solved_tasks_number),
                                                                            tasks_number=str(tasks_number)))
    return None, None


CALLBACK_HANDLING_FUNCTION: dict[str, Callable[[Any, int, int, list[str]], tuple[Optional[Callable], Any]]] = {
    inline_markups.CALLBACK_DATA_NONE: compute_none_callback,
    inline_markups.CALLBACK_DATA_SHOW_RESULTS_TABLE: compute_show_results_table_callback,
    inline_markups.CALLBACK_DATA_FROM_LOGIN_IN_RESULTS_TABLE: compute_show_login_in_results_table_callback
}
