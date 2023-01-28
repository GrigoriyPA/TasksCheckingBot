from bot import constants
from bot.entities.homework import Homework
from bot.entities.result import Result
from bot.telegram_logic import handling_functions
from bot.telegram_logic.client.inner_types import Attachment
from bot.telegram_logic.interface import inline_markups, keyboard_markups, messages_text
from collections.abc import Callable
from typing import Any, Optional


def __get_solver_task_cell_description(handler, from_id, login, task_id, correct_answers, answer) -> str:
    correct_answer_text = str(correct_answers[0])
    for right_answer in correct_answers[1:]:
        correct_answer_text += messages_text.RIGHT_ANSWERS_SPLITER + str(right_answer)

    if answer is None:
        if handler.is_admin(from_id):
            return messages_text.MESSAGE_ON_CELL_OF_NOT_SOLVED_TASK_IN_TABLE_FOR_ADMIN.format(login=login,
                                                                                              task_id=str(task_id),
                                                                                              correct_answer=correct_answer_text)
        return messages_text.MESSAGE_ON_CELL_OF_NOT_SOLVED_TASK_IN_TABLE_FOR_STUDENT.format(task_id=str(task_id))

    if answer.text_answer in correct_answers:
        if handler.is_admin(from_id):
            return messages_text.MESSAGE_ON_CELL_OF_RIGHT_SOLVED_TASK_IN_TABLE_FOR_ADMIN.format(login=login,
                                                                                                task_id=str(task_id),
                                                                                                answer=answer.text_answer)
        return messages_text.MESSAGE_ON_CELL_OF_RIGHT_SOLVED_TASK_IN_TABLE_FOR_STUDENT.format(task_id=str(task_id),
                                                                                              answer=answer.text_answer)

    if handler.is_admin(from_id):
        return messages_text.MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_ADMIN.format(login=login,
                                                                                            task_id=str(task_id),
                                                                                            correct_answer=correct_answer_text,
                                                                                            answer=answer.text_answer)
    return messages_text.MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_STUDENT.format(task_id=str(task_id),
                                                                                          correct_answer=correct_answer_text,
                                                                                          answer=answer.text_answer)


def compute_callback(handler, from_id: int, message_id: int, text: str, callback_data: str) -> tuple[Optional[Callable], Any]:
    # If user is not authorized, reject chooses
    if not handler.is_authorized(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNAUTHORIZED_USER)
        return None, None

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

    exercise_name = callback_data[0]  # Getting stored exercise name
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Creating table of results
    markup = inline_markups.get_results_table_inline_markup(
        handler.get_results_of_students_by_exercise_name(exercise_name), exercise_name,
        len(exercise_info.tasks), 1)

    # Sending table
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_SUCCESS_CREATION_TABLE.format(exercise_name=exercise_name,
                                                                       grade=str(exercise_info.grade)),
                         markup=markup)
    return None, None


def compute_show_login_in_results_table_callback(handler, from_id: int, message_id: int, text: str,
                                                 callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user wants to see statistic of one user in results table

    login, exercise_name = callback_data[0], callback_data[1]  # Getting chooses login and exercise name
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Calculation number of right solved tasks
    tasks_number = len(exercise_info.tasks)
    solved_tasks_number = handler.get_number_of_right_answers_on_task(login, exercise_name)

    # Send statistic
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_SHOW_LOGIN_IN_RESULTS_TABLE.format(login=login,
                                                                            solved_tasks_number=str(solved_tasks_number),
                                                                            tasks_number=str(tasks_number)))
    return None, None


def compute_cell_of_task_in_table_callback(handler, from_id: int, message_id: int, text: str,
                                           callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user chooses task for see right answer on this task (in results table)

    user = handler.get_user_info_by_id(from_id)

    # Getting chooses user login, homework name and task id
    login, exercise_name, task_id = callback_data[0], callback_data[1], int(callback_data[2])
    exercise_info: Homework = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # If user is not admin, and he want to see someone else's answer, reject choice
    if not handler.is_admin(from_id) and login != user.login:
        return None, None

    # Getting user answer on current task
    answer: Optional[Result] = handler.get_user_answer_on_task(login, exercise_name, task_id)
    correct_answers = handler.get_right_answer_on_task(exercise_name, task_id)

    # If task was blocked or deleted, reject choice
    if correct_answers is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_TASK)
        return None, None

    correct_answer_text = str(correct_answers[0])
    for right_answer in correct_answers[1:]:
        correct_answer_text += messages_text.RIGHT_ANSWERS_SPLITER + str(right_answer)

    # Create solved task options markup
    markup = inline_markups.get_solved_task_description_actions_inline_markup(login, exercise_info, task_id, answer,
                                                                              correct_answers,
                                                                              handler.is_admin(from_id))

    # Show right answer
    text = __get_solver_task_cell_description(handler, from_id, login, task_id, correct_answers, answer)
    handler.send_message(send_id=from_id, text=text, markup=markup)
    return None, None


def compute_refresh_results_table_callback(handler, from_id: int, message_id: int, text: str,
                                           callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user wants to refresh results table

    # Getting chooses homework name and last first task id
    exercise_name, first_task_id = callback_data[0], int(callback_data[1])
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Update results table
    markup = inline_markups.get_results_table_inline_markup(
        handler.get_results_of_students_by_exercise_name(exercise_name), exercise_name,
        len(exercise_info.tasks), first_task_id)

    if not handler.edit_message(from_id=from_id, message_id=message_id, text=text, markup=markup):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ALREADY_ACTUAL_INFORMATION_IN_RESULTS_TABLE)
    return None, None


def compute_switch_results_table_callback(handler, from_id: int, message_id: int, text: str,
                                          callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user wants to switch page in results table

    # Getting chooses homework name and last first task id
    exercise_name, first_task_id = callback_data[0], int(callback_data[1])
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Update results table
    markup = inline_markups.get_results_table_inline_markup(
        handler.get_results_of_students_by_exercise_name(exercise_name), exercise_name,
        len(exercise_info.tasks), first_task_id)

    handler.edit_message(from_id=from_id, message_id=message_id, text=text, markup=markup)
    return None, None


def compute_select_homework_for_send_answer_callback(handler, from_id: int, message_id: int, text: str,
                                                     callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user chooses homework for solve (in list of homeworks)

    # If user is not student, reject choice
    if not handler.is_student(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_STUDENT_USER)
        return None, None

    exercise_name = callback_data[0]  # Getting chooses homework name
    user_info = handler.get_user_info_by_id(from_id)
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None or exercise_info.grade != user_info.grade:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Creating table of tasks
    markup = inline_markups.get_student_task_list_inline_markup(user_info.login, exercise_info, handler.check_task)
    handler.send_message(send_id=from_id, text=messages_text.TOP_MESSAGE_OF_STUDENT_TASK_LIST, markup=markup)
    return None, None


def compute_select_task_id_for_send_answer_callback(handler, from_id: int, message_id: int, text: str,
                                                    callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user chooses task for solve (in list of tasks)

    # If user is not student, reject choice
    if not handler.is_student(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_STUDENT_USER)
        return None, None

    exercise_name, task_id = callback_data[0], int(callback_data[1])  # Getting chooses homework name and task id
    user_info = handler.get_user_info_by_id(from_id)
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None or exercise_info.grade != user_info.grade:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Update table of tasks
    markup = inline_markups.get_student_task_list_inline_markup(user_info.login, exercise_info, handler.check_task)
    handler.edit_message(from_id=from_id, message_id=message_id, text=text, markup=markup)

    # If task was blocked or deleted, reject choice
    if handler.check_task(user_info.login, exercise_name, task_id) is not None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_TASK)
        return None, None

    # Start waiting of answer for current task in current exercise
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_START_WAITING_ANSWER_ON_TASK.format(task_id=str(task_id)),
                         markup=keyboard_markups.get_back_button_keyboard())
    return handling_functions.solving_task_waiting_answer, (exercise_name, task_id)


def compute_select_student_grade_for_create_callback(handler, from_id: int, message_id: int, text: str,
                                                     callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin wants to create new student account

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    grade = int(callback_data[0])  # Getting chooses grade

    # Start waiting of login for create new student account
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_START_WAITING_LOGIN_OF_NEW_STUDENT_ACCOUNT,
                         markup=keyboard_markups.get_back_button_keyboard())
    return handling_functions.adding_student_waiting_login, grade


def compute_select_exercise_grade_for_create_callback(handler, from_id: int, message_id: int, text: str,
                                                      callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin wants to create new exercise

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    grade = int(callback_data[0])  # Getting chooses grade

    # Start waiting of exercise name for create
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_START_WAITING_EXERCISE_NAME_FOR_CREATE,
                         markup=keyboard_markups.get_back_button_keyboard())
    return handling_functions.adding_exercise_waiting_exercise_name, (grade, False)


def compute_select_quest_grade_for_create_callback(handler, from_id: int, message_id: int, text: str,
                                                   callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin wants to create new quest

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    grade = int(callback_data[0])  # Getting chooses grade

    # TODO check chooses grade

    # Start waiting of exercise name for create
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_START_WAITING_QUEST_NAME_FOR_CREATE,
                         markup=keyboard_markups.get_back_button_keyboard())
    return handling_functions.adding_exercise_waiting_exercise_name, (grade, True)


def compute_show_exercise_description_callback(handler, from_id: int, message_id: int, text: str,
                                               callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin chooses some exercise for see its description (in list of exercises)

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    exercise_name = callback_data[0]  # Getting chooses exercise name
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Create and send description of current task
    handler.send_message(send_id=from_id,
                         text=messages_text.FIRST_MESSAGE_IN_EXERCISE_DESCRIPTION.format(grade=exercise_info.grade,
                                                                                         exercise_name=exercise_name),
                         markup=inline_markups.get_exercise_description_in_list_of_exercises_inline_markup(exercise_info))
    return None, None


def compute_account_action_show_password_callback(handler, from_id: int, message_id: int, text: str,
                                                  callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin chooses some user for see his password (in list of logins)

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    login = callback_data[0]  # Getting chooses user login
    user_info = handler.get_user_info_by_login(login)

    # If current user was deleted, reject choice
    if user_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_LOGIN)
        return None, None

    # Not super-admin can not see passwords of other admins
    if login != handler.get_user_info_by_id(from_id).login and not handler.is_super_admin(from_id) \
            and not user_info.status == constants.STUDENT_STATUS:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    # Show user password
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_WITH_PASSWORD_DESCRIPTION.format(login=login,
                                                                                        password=user_info.password))
    return None, None


def compute_account_action_show_user_callback(handler, from_id: int, message_id: int, text: str,
                                              callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin wants to see current user on chooses login (in list of logins)

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    login = callback_data[0]  # Getting chooses user login
    user_info = handler.get_user_info_by_login(login)

    # If current user was deleted, reject choice
    if user_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_LOGIN)
        return None, None

    # If there is no user on chooses login
    if user_info.telegram_id == constants.UNAUTHORIZED_TELEGRAM_ID:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNAUTHORIZED_USER_LOGIN)
        return None, None

    # Show user telegram info
    current_user_info = handler.get_chat_member(user_info.telegram_id, user_info.telegram_id).user
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_WITH_USER_TELEGRAM_INFO.format(first_name=current_user_info.first_name,
                                                                     last_name=current_user_info.last_name,
                                                                     username=current_user_info.username))
    return None, None


def compute_student_account_action_show_results_callback(handler, from_id: int, message_id: int, text: str,
                                                         callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin wants to see results of chooses user (in list of logins)

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    login = callback_data[0]  # Getting chooses user login
    user_info = handler.get_user_info_by_login(login)

    # If current user was deleted, reject choice
    if user_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_LOGIN)
        return None, None

    homeworks = handler.get_all_exercises_names_for_grade(user_info.grade)
    homeworks_names = []
    for homework in homeworks:
        homeworks_names.append(homework.name)

    user_results = handler.get_user_results_on_exercises(login, homeworks_names)

    # Create table of user results and send results
    markup = inline_markups.get_user_results_table_inline_markup(homeworks_names, user_results)
    handler.send_message(send_id=from_id, text=messages_text.TOP_MESSAGE_OF_USER_RESULTS_TABLE.format(login=login), markup=markup)
    return None, None


def compute_show_task_statement_callback(handler, from_id: int, message_id: int, text: str,
                                         callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin wants to see results of chooses user (in list of logins)

    exercise_name, task_id = callback_data[0], int(callback_data[1])  # Getting chooses exercise name, task id
    exercise_info = handler.get_exercise_info_by_name(exercise_name)
    user_info = handler.get_user_info_by_id(from_id)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None or (not handler.is_admin(from_id) and exercise_info.grade != user_info.grade):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    text_statement = exercise_info.tasks[task_id - 1].text_statement
    text = messages_text.MESSAGE_WITH_FILE_EXERCISE_STATEMENT.format(task_id=str(task_id))
    if text_statement != "":
        text = messages_text.MESSAGE_WITH_TEXT_EXERCISE_STATEMENT.format(task_id=str(task_id),
                                                                         text_statement=text_statement)

    # Send exercise statement
    attachment_data, attachment_ext = exercise_info.tasks[task_id - 1].file_statement
    if attachment_data != bytes():
        handler.send_message(send_id=from_id, text=text,
                             attachments=[Attachment(data=attachment_data,
                                                     file_name=messages_text.STATEMENT_FILE_NAME + "." + attachment_ext)])
    else:
        handler.send_message(send_id=from_id, text=text)

    return None, None


def compute_solved_task_description_action_show_explanation_callback(handler, from_id: int, message_id: int, text: str,
                                                                     callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user wants to see explanation of chooses task (in solved task description)

    user = handler.get_user_info_by_id(from_id)

    # Getting chooses user login, homework name and task id
    login, exercise_name, task_id = callback_data[0], callback_data[1], int(callback_data[2])
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # If user is not admin, and he want to see someone else's answer, reject choice
    if not handler.is_admin(from_id) and login != user.login:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    # Getting user answer on current task
    answer: Optional[Result] = handler.get_user_answer_on_task(login, exercise_name, task_id)

    # If task was blocked or deleted, reject choice
    if answer is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNAVAILABLE_ANSWER_EXPLANATION)
        return None, None

    # Getting text explanation
    text_explanation = answer.text_clarification
    if handler.is_admin(from_id):
        text = messages_text.MESSAGE_WITH_TASK_FILE_EXPLANATION_FOR_ADMIN.format(login=login, task_id=str(task_id))
        if text_explanation != "":
            text = messages_text.MESSAGE_WITH_TASK_TEXT_EXPLANATION_FOR_ADMIN.format(login=login, task_id=str(task_id),
                                                                       text_explanation=text_explanation)
    else:
        text = messages_text.MESSAGE_WITH_TASK_FILE_EXPLANATION_FOR_STUDENT.format(task_id=str(task_id))
        if text_explanation != "":
            text = messages_text.MESSAGE_WITH_TASK_TEXT_EXPLANATION_FOR_STUDENT.format(task_id=str(task_id),
                                                                       text_explanation=text_explanation)

    # Getting explanation file and send explanation
    attachment_data, attachment_ext = answer.file_answer
    if attachment_data != bytes():
        handler.send_message(send_id=from_id, text=text,
                             attachments=[Attachment(data=attachment_data,
                                                     file_name=messages_text.EXPLANATION_FILE_NAME + "." + attachment_ext)])
    else:
        handler.send_message(send_id=from_id, text=text)

    return None, None


def compute_solved_task_description_action_switch_student_answer_callback(handler, from_id: int, message_id: int, text: str,
                                                                          callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when user wants to see explanation of chooses task (in solved task description)

    # Getting chooses user login, homework name and task id
    login, exercise_name, task_id = callback_data[0], callback_data[1], int(callback_data[2])
    exercise_info = handler.get_exercise_info_by_name(exercise_name)
    user_info = handler.get_user_info_by_login(login)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Getting user answer on current task
    answer: Optional[Result] = handler.get_user_answer_on_task(login, exercise_name, task_id)
    correct_answers = handler.get_right_answer_on_task(exercise_name, task_id)

    # If task was blocked or deleted, reject choice
    if correct_answers is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_TASK)
        return None, None

    if handler.is_admin(from_id):
        # Switch user answer and create notification
        if answer is None or answer.text_answer not in correct_answers:
            notification = messages_text.MESSAGE_NOTIFICATION_FOR_STUDENT_ON_ACCEPTED_TASK.format(exercise_name=exercise_name,
                                                                                                 task_id=str(task_id))
            if answer is None:
                handler.send_answer_on_exercise(login, {"exercise_name": exercise_name, "task_id": task_id,
                                                     "answer": correct_answers[0], "explanation_text": "",
                                                     "explanation_data": bytes(), "explanation_ext": ""})
            else:
                handler.change_user_answer_on_exercise(login, exercise_name, task_id, correct_answers[0])
        else:
            notification = messages_text.MESSAGE_NOTIFICATION_FOR_STUDENT_ON_REJECTED_TASK.format(exercise_name=exercise_name,
                                                                                                 task_id=str(task_id))
            handler.change_user_answer_on_exercise(login, exercise_name, task_id, "")
        answer: Optional[Result] = handler.get_user_answer_on_task(login, exercise_name, task_id)

        # Send notification for current user on student account, if he exists
        if user_info.telegram_id != constants.UNAUTHORIZED_TELEGRAM_ID:
            handler.send_message(send_id=user_info.telegram_id, text=notification)

    # Create and update solved task options markup
    markup = inline_markups.get_solved_task_description_actions_inline_markup(login, exercise_info, task_id, answer,
                                                                              correct_answers,
                                                                              handler.is_admin(from_id))
    handler.edit_message(from_id=from_id, message_id=message_id,
                         text=__get_solver_task_cell_description(handler, from_id, login, task_id, correct_answers, answer),
                         markup=markup)

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_SUCCESS_SWITCH_STUDENT_ANSWER)
    return None, None


def compute_show_right_answers_on_task_callback(handler, from_id: int, message_id: int, text: str,
                                                callback_data: list[str]) -> tuple[Optional[Callable], Any]:
    # This function is called when admin wants to see right answer on task (in task description from task list)

    # If user is not admin, reject choice
    if not handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_NOT_ADMIN_USER)
        return None, None

    # Getting chooses user login, homework name and task id
    exercise_name, task_id = callback_data[0], int(callback_data[1])
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If homework was blocked or deleted, reject choice
    if exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_EXERCISE_NAME)
        return None, None

    # Getting correct answers on current task
    correct_answers = handler.get_right_answer_on_task(exercise_name, task_id)

    # If task was blocked or deleted, reject choice
    if correct_answers is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_TASK)
        return None, None

    correct_answer_text = str(correct_answers[0])
    for right_answer in correct_answers[1:]:
        correct_answer_text += messages_text.RIGHT_ANSWERS_SPLITER + str(right_answer)

    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_WITH_LIST_OF_RIGHT_ANSWERS_ON_TASK.format(task_id=str(task_id),
                                                                                              correct_answer=correct_answer_text))
    return None, None


CALLBACK_HANDLING_FUNCTION: dict[str, Callable[[Any, int, int, str, list[str]], tuple[Optional[Callable], Any]]] = {
    inline_markups.CALLBACK_DATA_NONE: compute_none_callback,
    inline_markups.CALLBACK_DATA_SHOW_RESULTS_TABLE: compute_show_results_table_callback,
    inline_markups.CALLBACK_DATA_FROM_LOGIN_IN_RESULTS_TABLE: compute_show_login_in_results_table_callback,
    inline_markups.CALLBACK_DATA_FROM_CELL_OF_TASK: compute_cell_of_task_in_table_callback,
    inline_markups.CALLBACK_DATA_REFRESH_RESULTS_TABLE: compute_refresh_results_table_callback,
    inline_markups.CALLBACK_DATA_MOVE_RESULTS_TABLE: compute_switch_results_table_callback,
    inline_markups.CALLBACK_DATA_SELECT_HOMEWORK_FOR_SEND_ANSWER: compute_select_homework_for_send_answer_callback,
    inline_markups.CALLBACK_DATA_SELECT_EXERCISE_FOR_SEND_ANSWER: compute_select_task_id_for_send_answer_callback,
    inline_markups.CALLBACK_DATA_SELECT_STUDENT_GRADE_FOR_CREATE: compute_select_student_grade_for_create_callback,
    inline_markups.CALLBACK_DATA_SELECT_EXERCISE_GRADE_FOR_CREATE: compute_select_exercise_grade_for_create_callback,
    inline_markups.CALLBACK_DATA_SELECT_QUEST_GRADE_FOR_CREATE: compute_select_quest_grade_for_create_callback,
    inline_markups.CALLBACK_DATA_SHOW_EXERCISE_DESCRIPTION: compute_show_exercise_description_callback,
    inline_markups.CALLBACK_DATA_ACCOUNT_ACTION_SHOW_PASSWORD: compute_account_action_show_password_callback,
    inline_markups.CALLBACK_DATA_ACCOUNT_ACTION_SHOW_USER: compute_account_action_show_user_callback,
    inline_markups.CALLBACK_DATA_STUDENT_ACCOUNT_ACTION_SHOW_RESULTS: compute_student_account_action_show_results_callback,
    inline_markups.CALLBACK_DATA_SHOW_TASK_STATEMENT: compute_show_task_statement_callback,
    inline_markups.CALLBACK_DATA_SOLVED_TASK_DESCRIPTION_ACTION_SHOW_EXPLANATION: compute_solved_task_description_action_show_explanation_callback,
    inline_markups.CALLBACK_DATA_SOLVED_TASK_DESCRIPTION_ACTION_SWITCH_STUDENT_ANSWER: compute_solved_task_description_action_switch_student_answer_callback,
    inline_markups.CALLBACK_DATA_SHOW_RIGHT_ANSWERS_ON_TASK: compute_show_right_answers_on_task_callback
}
