from bot.telegram_logic import inline_markups, keyboard_markups, handling_functions
from collections.abc import Callable
from typing import Any, Optional

# common
MESSAGE_ON_UNAUTHORIZED_USER = "Вы не авторизованы."
MESSAGE_ON_NOT_STUDENT_USER = "Выбор задания невозможен."
MESSAGE_ON_NOT_ADMIN_USER = "Вы не обладаете достаточными правами."
MESSAGE_ON_UNKNOWN_EXERCISE_NAME = "Выбранная работа недоступна."
MESSAGE_ON_INVALID_TASK = "Выбранное задание недоступно."

# compute_show_results_table_callback
MESSAGE_ON_SUCCESS_CREATION_TABLE = "Текущие результаты по работе '{exercise_name}', {grade} класс:"

# compute_show_login_in_results_table_callback
MESSAGE_ON_SHOW_LOGIN_IN_RESULTS_TABLE = "{login}\nРешено {solved_tasks_number} / {tasks_number} задач."

# compute_cell_of_solved_task_in_table_callback
MESSAGE_ON_CELL_OF_RIGHT_SOLVED_TASK_IN_TABLE_FOR_ADMIN = "Правильный ответ '{login}' на задание {task_id}: {answer}"
MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_ADMIN = "Правильный ответ на задание {task_id}: {correct_answer}\n" \
                                                          "Ответ '{login}' на задание: {answer}"
MESSAGE_ON_CELL_OF_RIGHT_SOLVED_TASK_IN_TABLE_FOR_STUDENT = "Ваш правильный ответ на задание {task_id}: {answer}"
MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_STUDENT = "Правильный ответ на задание {task_id}: {correct_answer}\n" \
                                                            "Ваш ответ на задание:  {answer}"

# compute_refresh_results_table_callback
MESSAGE_ON_ALREADY_ACTUAL_INFORMATION_IN_RESULTS_TABLE = "Информация актуальна."

# compute_select_homework_for_send_answer_callback
TOP_MESSAGE_OF_STUDENT_TASK_LIST = "Выберите задание."

# compute_select_task_id_for_send_answer_callback
MESSAGE_ON_START_WAITING_ANSWER_ON_TASK = "Введите ответ на задание {task_id}:"

# compute_select_student_grade_for_create_callback
MESSAGE_ON_START_WAITING_LOGIN_OF_NEW_STUDENT_ACCOUNT = "Введите логин для нового аккаунта " \
                                                        "(доступны латинские символы, цифры и знаки препинания):"

# compute_select_exercise_grade_for_create_callback
MESSAGE_ON_START_WAITING_EXERCISE_NAME_FOR_CREATE = "Введите название новой работы " \
                                                    "(доступны латинские символы, цифры и знаки препинания):"

# compute_show_exercise_description_callback
FIRST_MESSAGE_IN_EXERCISE_DESCRIPTION = "Класс работы: {grade}\nВсего задач: {number_tasks}\nПравильные ответы:\n"


def compute_callback(handler, from_id: int, message_id: int, text: str, callback_data: str) -> tuple[Optional[Callable], Any]:
    # Parsing callback data
    callback_type = callback_data[0]
    callback_data = callback_data[1:].split(inline_markups.CALLBACK_SEPARATION_ELEMENT)

    return CALLBACK_HANDLING_FUNCTION[callback_type](handler, from_id, message_id, text, callback_data)


# Callback computing functions

def compute_none_callback(handler, from_id: int, message_id: int, text: str,
                          callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # Do nothing
    return None, None


def compute_show_results_table_callback(handler, from_id: int, message_id: int, text: str,
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


def compute_show_login_in_results_table_callback(handler, from_id: int, message_id: int, text: str,
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


def compute_cell_of_solved_task_in_table_callback(handler, from_id: int, message_id: int, text: str,
                                                  callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user chooses task for see right answer on this task (in results table)

    user = handler.get_user_info_by_id(from_id)

    # If user is not authorized, reject choice
    if user is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNAUTHORIZED_USER)
        return None, None

    # Getting chooses user login, homework name and task id
    login, exercise_name, task_id = callback_data[0], callback_data[1], int(callback_data[2])
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # If user is not admin, and he want to see someone else's answer, reject choice
    if not handler.is_admin(from_id) and login != user.login:
        return None, None

    # Getting user answer on current task
    answer = handler.get_user_answer_on_task(login, exercise_name, task_id)
    correct_answer = handler.get_right_answer_on_task(exercise_name, task_id)

    # If task was blocked or deleted, reject choice
    if answer is None or correct_answer is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_INVALID_TASK)
        return None, None

    # Show right answer
    if answer == correct_answer:
        if handler.is_admin(from_id):
            handler.send_message(send_id=from_id,
                                 text=MESSAGE_ON_CELL_OF_RIGHT_SOLVED_TASK_IN_TABLE_FOR_ADMIN.format(login=login,
                                                                                                     task_id=str(task_id),
                                                                                                     answer=answer))
        else:
            handler.send_message(send_id=from_id,
                                 text=MESSAGE_ON_CELL_OF_RIGHT_SOLVED_TASK_IN_TABLE_FOR_STUDENT.format(task_id=str(task_id),
                                                                                                       answer=answer))
    else:
        if handler.is_admin(from_id):
            handler.send_message(send_id=from_id,
                                 text=MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_ADMIN.format(login=login,
                                                                                                     task_id=str(task_id),
                                                                                                     correct_answer=correct_answer,
                                                                                                     answer=answer))
        else:
            handler.send_message(send_id=from_id,
                                 text=MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_STUDENT.format(task_id=str(task_id),
                                                                                                       correct_answer=correct_answer,
                                                                                                       answer=answer))
    return None, None


def compute_refresh_results_table_callback(handler, from_id: int, message_id: int, text: str,
                                           callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user wants to refresh results table

    # If user is not authorized, reject choice
    if not handler.is_authorized(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNAUTHORIZED_USER)
        return None, None

    # Getting chooses homework name and last first task id
    exercise_name, first_task_id = callback_data[0], int(callback_data[1])
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Update results table
    markup = inline_markups.get_results_table_inline_markup(
        handler.get_results_of_students_by_exercise_name(exercise_name), exercise_name,
        len(exercise_info.right_answers), first_task_id)

    if not handler.edit_message(from_id=from_id, message_id=message_id, text=text, markup=markup):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_ALREADY_ACTUAL_INFORMATION_IN_RESULTS_TABLE)
    return None, None


def compute_switch_results_table_callback(handler, from_id: int, message_id: int, text: str,
                                          callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user wants to switch page in results table

    # If user is not authorized, reject choice
    if not handler.is_authorized(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNAUTHORIZED_USER)
        return None, None

    # Getting chooses homework name and last first task id
    exercise_name, first_task_id = callback_data[0], int(callback_data[1])
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Update results table
    markup = inline_markups.get_results_table_inline_markup(
        handler.get_results_of_students_by_exercise_name(exercise_name), exercise_name,
        len(exercise_info.right_answers), first_task_id)

    handler.edit_message(from_id=from_id, message_id=message_id, text=text, markup=markup)
    return None, None


def compute_select_homework_for_send_answer_callback(handler, from_id: int, message_id: int, text: str,
                                                     callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user chooses homework for solve (in list of homeworks)

    # If user is not student, reject choice
    if not handler.is_student(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_NOT_STUDENT_USER)
        return None, None

    exercise_name = callback_data[0]  # Getting chooses homework name
    user_info = handler.get_user_info_by_id(from_id)
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None or exercise_info.grade != user_info.grade:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Creating table of tasks
    markup = inline_markups.get_student_task_list_inline_markup(user_info.login, len(exercise_info.right_answers),
                                                                exercise_name, handler.check_task)
    handler.send_message(send_id=from_id, text=TOP_MESSAGE_OF_STUDENT_TASK_LIST, markup=markup)
    return None, None


def compute_select_task_id_for_send_answer_callback(handler, from_id: int, message_id: int, text: str,
                                                    callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user chooses task for solve (in list of tasks)

    # If user is not student, reject choice
    if not handler.is_student(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_NOT_STUDENT_USER)
        return None, None

    exercise_name, task_id = callback_data[0], int(callback_data[1])  # Getting chooses homework name and task id
    user_info = handler.get_user_info_by_id(from_id)
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None or exercise_info.grade != user_info.grade:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Update table of tasks
    markup = inline_markups.get_student_task_list_inline_markup(user_info.login, len(exercise_info.right_answers),
                                                                exercise_name, handler.check_task)
    handler.edit_message(from_id=from_id, message_id=message_id, text=text, markup=markup)

    # If task was blocked or deleted, reject choice
    if handler.check_task(user_info.login, exercise_name, task_id) is not None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_INVALID_TASK)
        return None, None

    # Start waiting of answer for current task in current exercise
    handler.send_message(send_id=from_id, text=MESSAGE_ON_START_WAITING_ANSWER_ON_TASK.format(task_id=str(task_id)),
                         markup=keyboard_markups.get_back_button_keyboard())
    return handling_functions.solving_task_waiting_answer, (exercise_name, task_id)


def compute_select_student_grade_for_create_callback(handler, from_id: int, message_id: int, text: str,
                                                     callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin wants to create new student account

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    grade = int(callback_data[0])  # Getting chooses grade

    # Start waiting of login for create new student account
    handler.send_message(send_id=from_id,
                         text=MESSAGE_ON_START_WAITING_LOGIN_OF_NEW_STUDENT_ACCOUNT,
                         markup=keyboard_markups.get_back_button_keyboard())
    return handling_functions.adding_student_waiting_login, grade


def compute_select_exercise_grade_for_create_callback(handler, from_id: int, message_id: int, text: str,
                                                      callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin wants to create new exercise

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    grade = int(callback_data[0])  # Getting chooses grade

    # Start waiting of exercise name for create
    handler.send_message(send_id=from_id,
                         text=MESSAGE_ON_START_WAITING_EXERCISE_NAME_FOR_CREATE,
                         markup=keyboard_markups.get_back_button_keyboard())
    return handling_functions.adding_exercise_waiting_exercise_name, grade


def compute_show_exercise_description_callback(handler, from_id: int, message_id: int, text: str,
                                               callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin chooses some exercise for see its description (in list of exercises)

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    exercise_name = callback_data[0]  # Getting chooses exercise name
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Create and send description of current task
    text = FIRST_MESSAGE_IN_EXERCISE_DESCRIPTION.format(grade=exercise_info.grade,
                                                        number_tasks=str(len(exercise_info.right_answers)))
    for i in range(len(exercise_info.right_answers)):
        text += str(i + 1) + ": " + exercise_info.right_answers[i] + "\n"

    handler.send_message(send_id=from_id, text=text)
    return None, None


CALLBACK_HANDLING_FUNCTION: dict[str, Callable[[Any, int, int, str, list[str]], tuple[Optional[Callable], Any]]] = {
    inline_markups.CALLBACK_DATA_NONE: compute_none_callback,
    inline_markups.CALLBACK_DATA_SHOW_RESULTS_TABLE: compute_show_results_table_callback,
    inline_markups.CALLBACK_DATA_FROM_LOGIN_IN_RESULTS_TABLE: compute_show_login_in_results_table_callback,
    inline_markups.CALLBACK_DATA_FROM_CELL_OF_SOLVED_TASK: compute_cell_of_solved_task_in_table_callback,
    inline_markups.CALLBACK_DATA_REFRESH_RESULTS_TABLE: compute_refresh_results_table_callback,
    inline_markups.CALLBACK_DATA_MOVE_RESULTS_TABLE: compute_switch_results_table_callback,
    inline_markups.CALLBACK_DATA_SELECT_HOMEWORK_FOR_SEND_ANSWER: compute_select_homework_for_send_answer_callback,
    inline_markups.CALLBACK_DATA_SELECT_EXERCISE_FOR_SEND_ANSWER: compute_select_task_id_for_send_answer_callback,
    inline_markups.CALLBACK_DATA_SELECT_STUDENT_GRADE_FOR_CREATE: compute_select_student_grade_for_create_callback,
    inline_markups.CALLBACK_DATA_SELECT_EXERCISE_GRADE_FOR_CREATE: compute_select_exercise_grade_for_create_callback,
    inline_markups.CALLBACK_DATA_SHOW_EXERCISE_DESCRIPTION: compute_show_exercise_description_callback
}
