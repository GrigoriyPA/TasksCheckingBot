from bot import constants
from bot.telegram_logic.interface import inline_markups, keyboard_markups, messages_text
from bot.telegram_logic.user_handler import UserHandler, check_new_name, MARKUP_TYPES
from typing import Any, Callable, Optional


# Special computing functions

# Checking back button (common interface)
def __compute_button_back(handler: UserHandler, from_id: int, text: str, markup: MARKUP_TYPES = None,
                          message_info: str = '') -> bool:
    if text != messages_text.BUTTON_BACK:
        # There is no back button pressed
        return False

    # Back button have pressed, go back from current state
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_EXIT_FROM_CURRENT_STATE + message_info, markup=markup)
    return True


# Checking exit button (common interface)
def __compute_button_exit(handler: UserHandler, from_id: int, text: str, markup: MARKUP_TYPES = None,
                          message_info: str = '') -> bool:
    if text != messages_text.BUTTON_EXIT:
        # There is no exit button pressed
        return False

    # Exit button have pressed, exit from current account
    handler.sign_out_user(from_id)
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_LOG_OUT_FROM_CURRENT_ACCOUNT + message_info, markup=markup)
    return True


# Checking status button (common interface)
def __compute_button_status(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != messages_text.BUTTON_SHOW_STATUS:
        # There is no exit button pressed
        return False

    # Status button have pressed, show status of current account
    user_info = handler.get_user_info_by_id(from_id)
    if user_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_STATUS_UNAUTHORIZED_ACCOUNT)
    elif user_info.status == constants.STUDENT_STATUS:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_STATUS_STUDENT_ACCOUNT.format(login=user_info.login,
                                                                                            password=user_info.password,
                                                                                            status=user_info.status,
                                                                                            grade=user_info.grade))
    else:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_STATUS_ADMIN_ACCOUNT.format(login=user_info.login,
                                                                                          password=user_info.password,
                                                                                          status=user_info.status))
    return True


# Checking show results table button (common interface)
def __compute_button_show_results_table(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != messages_text.BUTTON_SHOW_RESULTS_TABLE:
        # There is no show results table button pressed
        return False

    # Create list of exists homeworks
    markup = inline_markups.get_list_of_all_homeworks_inline_markup(handler.get_all_exercises_names(),
                                                                    inline_markups.CALLBACK_DATA_SHOW_RESULTS_TABLE)
    if markup is None:
        # There is no opened homeworks
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_COMMAND_SHOW_RESULTS_TABLE_NO_HOMEWORKS_OPENED)
    else:
        # Print list of exists homework
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_COMMAND_SHOW_RESULTS_TABLE, markup=markup)
    return True


# Checking admin get list of exercises button (default admin interface)
def __compute_button_admin_get_list_of_exercises(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != messages_text.BUTTON_EXERCISES_LIST:
        # There is no admin get list of exercises button pressed
        return False

    # Admin get list of exercises button have pressed, print list of exists exercises
    exercises_names = handler.get_all_exercises_names()
    exercises_names.sort()

    if len(exercises_names) == 0:
        # There is no homeworks created
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_GET_LIST_OF_EXERCISES_NO_HOMEWORKS_OPENED)
        return True

    # Send list of homeworks
    for name in exercises_names:
        handler.send_message(send_id=from_id, text=name, markup=inline_markups.get_exercise_actions_inline_markup(name))
    return True


# Checking admin get list of accounts button (default admin interface)
def __compute_button_admin_get_list_of_accounts(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != messages_text.BUTTON_ACCOUNTS_LIST:
        # There is no admin get list of accounts button pressed
        return False

    # Admin get list of accounts button have pressed, print list of exists accounts

    # Admins can see only other admins and users (not super-admins)
    if handler.is_super_admin(from_id):
        users = handler.get_users_info_by_status(constants.SUPER_ADMIN_STATUS)
        users.sort(key=lambda current_user: current_user.login)
        if len(users) > 0:
            # Send list of super-admins
            handler.send_message(send_id=from_id, text=messages_text.TOP_MESSAGE_OF_LIST_OF_SUPER_ADMINS)
            for user in users:
                handler.send_message(send_id=from_id, text=user.login,
                                     markup=inline_markups.get_admin_account_actions_inline_markup(user.login))

    users = handler.get_users_info_by_status(constants.ADMIN_STATUS)
    users.sort(key=lambda current_user: current_user.login)
    if len(users) > 0:
        # Send list of admins
        handler.send_message(send_id=from_id, text=messages_text.TOP_MESSAGE_OF_LIST_OF_ADMINS)
        for user in users:
            handler.send_message(send_id=from_id, text=user.login,
                                 markup=inline_markups.get_admin_account_actions_inline_markup(user.login))

    users = handler.get_users_info_by_status(constants.STUDENT_STATUS)
    users.sort(key=lambda current_user: current_user.login)
    if len(users) > 0:
        # Send list of students
        handler.send_message(send_id=from_id, text=messages_text.TOP_MESSAGE_OF_LIST_OF_STUDENTS)
        for user in users:
            handler.send_message(send_id=from_id,
                                 text=messages_text.STUDENT_DESCRIPTION_IN_LIST_OF_STUDENTS.format(login=user.login,
                                                                                     grade=str(user.grade)),
                                 markup=inline_markups.get_student_account_actions_inline_markup(user.login))
    return True


# Checking admin add action button (default admin interface)
def __compute_button_admin_add_action(handler: UserHandler, from_id: int, text: str,
                                      markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_ADD:
        # There is no admin add action button pressed
        return False

    # Admin add action button have pressed, update state and keyboard
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ADMIN_ADD_COMMAND, markup=markup)
    return True


# Checking admin delete action button (default admin interface)
def __compute_button_admin_delete_action(handler: UserHandler, from_id: int, text: str,
                                         markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_DELETE:
        # There is no admin delete action button pressed
        return False

    # Admin delete action button have pressed, update state and keyboard
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ADMIN_DELETE_COMMAND, markup=markup)
    return True


# Checking student send answer button (default student interface)
def __compute_button_student_send_answer(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != messages_text.BUTTON_SOLVE_EXERCISE:
        # There is no student send answer button pressed
        return False

    user_info = handler.get_user_info_by_id(from_id)

    # Create list of available homeworks
    if user_info is not None:
        markup = inline_markups.get_list_of_all_homeworks_inline_markup(
            handler.get_all_exercises_names_for_grade(user_info.grade),
            inline_markups.CALLBACK_DATA_SELECT_HOMEWORK_FOR_SEND_ANSWER)
    else:
        markup = None

    # Student send answer button have pressed, print list of available exercises
    if markup is None:
        # There is no available homeworks
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_STUDENT_SEND_ANSWER_NO_HOMEWORKS_AVAILABLE)
    else:
        # Print list of exists homework
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_STUDENT_SEND_ANSWER, markup=markup)
    return True


# Send correct answer, when student have solved task
def __send_correct_answer_to_student(handler: UserHandler, from_id: int, text: str, data,
                                     markup: MARKUP_TYPES = None) -> None:
    # Getting chooses exercise name, task id and answer
    exercise_name = data["exercise_name"]
    task_id = data["task_id"]
    answer = data["answer"]
    user_info = handler.get_user_info_by_id(from_id)
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If task was blocked or deleted, reject answer
    if user_info is None or exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_EXERCISE_NAME,
                             markup=markup)
        return

    correct_answers = handler.send_answer_on_exercise(user_info.login, data)

    correct_answer_text = str(correct_answers[0])
    for right_answer in correct_answers[1:]:
        correct_answer_text += messages_text.RIGHT_ANSWERS_SPLITER + str(right_answer)

    # Checking answer
    if answer in correct_answers:
        result = messages_text.MESSAGE_RIGHT_RESULT_MARK
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_RIGHT_ANSWER,
                             markup=markup)
    else:
        result = messages_text.MESSAGE_WRONG_RESULT_MARK
        handler.send_message(send_id=from_id,
                             text=messages_text.MESSAGE_ON_WRONG_ANSWER.format(correct_answer=correct_answer_text),
                             markup=markup)

    # Sending notifications to all admins
    for admin_info in handler.get_users_info_by_status(constants.ADMIN_STATUS) + \
                      handler.get_users_info_by_status(constants.SUPER_ADMIN_STATUS):
        # Scip all not authorized admins
        if admin_info.telegram_id == constants.UNAUTHORIZED_TELEGRAM_ID:
            continue

        handler.send_message(send_id=admin_info.telegram_id,
                             text=messages_text.NOTIFICATION_FOR_ADMINS_ON_SOLVED_TASK.format(login=user_info.login,
                                                                                              grade=user_info.grade,
                                                                                              exercise_name=exercise_name,
                                                                                              task_id=str(task_id),
                                                                                              answer=answer,
                                                                                              correct_answer=correct_answer_text,
                                                                                              result=result))


# Checking student want to send explanation (send explanation interface)
def __compute_button_student_want_to_send_explanation(handler: UserHandler, from_id: int, text: str, data,
                                                      markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_STUDENT_WANT_TO_SEND_EXPLANATION:
        # There is no student want to send explanation button pressed
        return False

    # Student want to send explanation button have pressed, change state
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_START_WAITING_EXPLANATION, markup=markup)
    return True


# Checking student do not want to send explanation (send explanation interface)
def __compute_button_student_do_not_want_to_send_explanation(handler: UserHandler, from_id: int, text: str, data,
                                                             markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_STUDENT_DO_NOT_WANT_TO_SEND_EXPLANATION:
        # There is no student do not want to send explanation button pressed
        return False

    # Student do not want to send explanation button have pressed, change state
    __send_correct_answer_to_student(handler, from_id, text, data, markup=markup)
    return True


# Checking admin add student button (adding admin interface)
def __compute_button_admin_add_student(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != messages_text.BUTTON_ADD_STUDENT:
        # There is no admin add student button pressed
        return False

    # Admin add student button have pressed, print list of all grades
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ADMIN_ADD_NEW_STUDENT,
                         markup=inline_markups.get_list_of_all_grades_inline_markup(
                                inline_markups.CALLBACK_DATA_SELECT_STUDENT_GRADE_FOR_CREATE))
    return True


# Checking admin add exercise button (adding admin interface)
def __compute_button_admin_add_exercise(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != messages_text.BUTTON_ADD_EXERCISE:
        # There is no admin add exercise button pressed
        return False

    # Admin add exercise button have pressed, print list of all grades
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ADMIN_ADD_NEW_EXERCISE,
                         markup=inline_markups.get_list_of_all_grades_inline_markup(
                                inline_markups.CALLBACK_DATA_SELECT_EXERCISE_GRADE_FOR_CREATE))
    return True


# Checking super-admin add admin account button (adding super-admin interface)
def __compute_button_super_admin_add_admin_account(handler: UserHandler, from_id: int, text: str,
                                                   markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_ADD_ADMIN:
        # There is no super-admin add admin account button pressed
        return False

    # Super-admin add admin account button have pressed, start waiting login of new account
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_SUPER_ADMIN_ADD_NEW_ADMIN, markup=markup)
    return True


# Checking adding answer for task in creation new exercise process button (adding exercise, task settings interface)
def __compute_button_adding_answer_for_task(handler: UserHandler, from_id: int, text: str, data,
                                            markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_ADD_ANSWER_ON_TASK:
        # There is no adding answer for task in creation new exercise process button pressed
        return False

    # Adding answer for task in creation new exercise process button have pressed, start waiting new answer
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_REQUEST_FOR_NEW_ANSWER.format(task_id=data["task_id"]),
                         markup=markup)
    return True


# Checking adding statement for task in creation new exercise process button (adding exercise, task settings interface)
def __compute_button_adding_statement_for_task(handler: UserHandler, from_id: int, text: str, data,
                                               markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_ADD_STATEMENT_FOR_TASK or data["task_id"] in data["task_statements"]:
        # There is no adding statement for task in creation new exercise process button pressed
        return False

    # Adding statement for task in creation new exercise process button have pressed, start waiting statement
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_ADD_STATEMENT_FOR_TASK,
                         markup=markup)
    return True


# Checking go to next task settings button (adding exercise, task settings interface)
def __compute_button_go_to_next_task_settings(handler: UserHandler, from_id: int, text: str, data) -> Optional[bool]:
    if text != messages_text.BUTTON_NEXT_TASK_IN_ADDING_TASK_INTERFACE or data["task_id"] == data["number_tasks"] or \
            data["task_id"] not in data["right_answers"]:
        # There is no go to next task settings button pressed
        return False

    # Go to next task settings button have pressed, switch interface
    data["task_id"] += 1
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_MOVE_INTO_TASK_ADDING_INTERFACE.format(task_id=data["task_id"]),
                         markup=keyboard_markups.get_adding_exercise_interface_keyboard(data["task_id"], data["number_tasks"],
                                                                                        data["task_id"] in data["right_answers"],
                                                                                        data["task_id"] in data["task_statements"],
                                                                                        data["number_unchecked_tasks"] == 0))
    return True


# Checking go to previous task settings button (adding exercise, task settings interface)
def __compute_button_go_to_previous_task_settings(handler: UserHandler, from_id: int, text: str,
                                                  data) -> Optional[bool]:
    if text != messages_text.BUTTON_PREVIOUS_TASK_IN_ADDING_TASK_INTERFACE or data["task_id"] == 1 or \
            data["task_id"] not in data["right_answers"]:
        # There is no go to previous task settings button pressed
        return False

    # Go to previous task settings button have pressed, switch interface
    data["task_id"] -= 1
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_MOVE_INTO_TASK_ADDING_INTERFACE.format(task_id=data["task_id"]),
                         markup=keyboard_markups.get_adding_exercise_interface_keyboard(data["task_id"], data["number_tasks"],
                                                                                        data["task_id"] in data["right_answers"],
                                                                                        data["task_id"] in data["task_statements"],
                                                                                        data["number_unchecked_tasks"] == 0))
    return True


# Checking finish creating new exercise button (adding exercise, task settings interface)
def __compute_button_finish_creating_new_exercise(handler: UserHandler, from_id: int, text: str, data,
                                                  markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_FINISH_CREATING_EXERCISE or data["number_unchecked_tasks"] > 0:
        # There is no finish creating new exercise button pressed
        return False

    # Finish creating new exercise button have pressed, start waiting new answer
    handler.add_exercise(data)
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_SUCCESS_CREATION_OF_NEW_EXERCISE)
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_ADMIN_ADD_COMMAND,
                         markup=markup)
    return True


# Checking admin delete account button (deleting admin interface)
def __compute_button_admin_delete_account(handler: UserHandler, from_id: int, text: str,
                                          markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_DELETE_ACCOUNT:
        # There is no admin delete account button pressed
        return False

    # Admin delete account button have pressed, start waiting login of deletion account
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ADMIN_DELETE_ACCOUNT, markup=markup)
    return True


# Checking admin delete exercise button (deleting admin interface)
def __compute_button_admin_delete_exercise(handler: UserHandler, from_id: int, text: str,
                                           markup: MARKUP_TYPES = None) -> bool:
    if text != messages_text.BUTTON_DELETE_EXERCISE:
        # There is no admin delete exercise button pressed
        return False

    # Admin delete exercise button have pressed, start waiting name of deletion exercise
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ADMIN_DELETE_EXERCISE, markup=markup)
    return True


# Bot state functions

# Initial state
def default_state(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called on first user message to bot (in current session)

    if handler.is_admin(from_id):
        # Current user is admin, go to admin home page
        handler.send_message(send_id=from_id, text=messages_text.WELCOME_MESSAGE_FOR_ADMIN,
                             markup=keyboard_markups.get_default_admin_keyboard())
        return default_admin_page, None

    if handler.is_student(from_id):
        # Current user is student, go to student home page
        handler.send_message(send_id=from_id, text=messages_text.WELCOME_MESSAGE_FOR_STUDENT,
                             markup=keyboard_markups.get_default_student_keyboard())
        return default_student_page, None

    # Current user is unauthorized, start waiting of login for authorization
    handler.send_message(send_id=from_id, text=messages_text.WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS,
                         markup=keyboard_markups.remove_keyboard())
    return unauthorized_user_waiting_login, None


# Authorization branch
def unauthorized_user_waiting_login(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when user wants to authorize (waiting login)

    login: str = text  # Current login

    # If there is no such login, reset authorization
    if not handler.is_exists_login(login):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_LOGIN)
        return unauthorized_user_waiting_login, None

    # Start waiting of password for authorizing in current login
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_VALID_LOGIN,
                         markup=keyboard_markups.get_back_button_keyboard())
    return unauthorized_user_waiting_password, login


def unauthorized_user_waiting_password(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when user wants to authorize (waiting password, login stored in data)

    if __compute_button_back(handler, from_id, text, keyboard_markups.remove_keyboard(),
                             message_info=messages_text.WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS):
        return unauthorized_user_waiting_login, None

    login: str = data  # Current login
    password: str = text  # Current password

    # If password is incorrect, reset authorization
    if not handler.is_valid_password(login, password):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_PASSWORD)
        return unauthorized_user_waiting_password, login

    user = handler.get_user_info_by_login(login)

    # Send notification for last user on current login, if he exists
    if user.telegram_id != constants.UNAUTHORIZED_TELEGRAM_ID:
        handler.send_message(send_id=user.telegram_id, text=messages_text.NOTIFICATION_FOR_LAST_USER_ON_AUTHORIZED_ACCOUNT,
                             markup=keyboard_markups.remove_keyboard())
        handler.update_user_state(user.telegram_id, unauthorized_user_waiting_login, None)

    handler.sign_in_user(login, from_id)  # Authorize current user

    if handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_SUCCESS_ADMIN_AUTHORIZATION,
                             markup=keyboard_markups.get_default_admin_keyboard())
        return default_admin_page, None

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_SUCCESS_STUDENT_AUTHORIZATION,
                         markup=keyboard_markups.get_default_student_keyboard())
    return default_student_page, None


# Initial student interface
def default_student_page(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_exit(handler, from_id, text, keyboard_markups.remove_keyboard(),
                             message_info=messages_text.WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS):
        return unauthorized_user_waiting_login, None

    if __compute_button_status(handler, from_id, text):
        return default_student_page, None

    if __compute_button_show_results_table(handler, from_id, text):
        return default_student_page, None

    if __compute_button_student_send_answer(handler, from_id, text):
        return default_student_page, None

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_COMMAND)
    return default_student_page, None


# Solving task branch
def solving_task_waiting_answer(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called on user input during waiting answer on some exercise

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_default_student_keyboard()):
        return default_student_page, None

    exercise_name, task_id = data[0], int(data[1])  # Getting chooses exercise name and task id
    user_info = handler.get_user_info_by_id(from_id)
    exercise_info = handler.get_exercise_info_by_name(exercise_name)

    # If task was blocked or deleted, reject answer
    if user_info is None or exercise_info is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_EXERCISE_NAME,
                             markup=keyboard_markups.get_default_student_keyboard())
        return default_student_page, None

    answer = text

    # Empty answer are banned
    if answer == '':
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_ANSWER)
        return solving_task_waiting_answer, data

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_MOVING_IN_EXPLANATION_SENDING_INTERFACE,
                         markup=keyboard_markups.get_student_send_explanation_keyboard())
    return solving_task_send_explanation_interface, {"exercise_name": exercise_name, "task_id": task_id,
                                                     "answer": answer, "explanation_text": "",
                                                     "explanation_data": bytes(), "explanation_ext": ""}


def solving_task_send_explanation_interface(handler: UserHandler, from_id: int, text: str,
                                            data) -> tuple[Callable, Any]:
    if __compute_button_student_want_to_send_explanation(handler, from_id, text, data,
                                                         markup=keyboard_markups.get_back_button_keyboard()):
        return solving_task_waiting_explanation, data

    if __compute_button_student_do_not_want_to_send_explanation(handler, from_id, text, data,
                                                                markup=keyboard_markups.get_default_student_keyboard()):
        return default_student_page, None

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_COMMAND)
    return solving_task_send_explanation_interface, data


def solving_task_waiting_explanation(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called on user input during waiting explanation of answer on some exercise

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_student_send_explanation_keyboard(),
                             message_info=messages_text.MESSAGE_ON_MOVING_IN_EXPLANATION_SENDING_INTERFACE):
        return solving_task_send_explanation_interface, data

    # Getting answer explanation
    data["explanation_text"] = text
    data["explanation_data"] = bytes()
    data["explanation_ext"] = ""

    attachment = handler.current_user_attachment[from_id]
    if attachment is not None:
        data["explanation_data"] = attachment.get_content()
        data["explanation_ext"] = attachment.get_extension()

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_SUCCESS_ADDED_EXPLANATION)
    __send_correct_answer_to_student(handler, from_id, text, data,
                                     markup=keyboard_markups.get_default_student_keyboard())
    return default_student_page, None


# Initial admin interface
def default_admin_page(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_exit(handler, from_id, text, keyboard_markups.remove_keyboard(),
                             message_info=messages_text.WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS):
        return unauthorized_user_waiting_login, None

    if __compute_button_status(handler, from_id, text):
        return default_admin_page, None

    if __compute_button_admin_add_action(handler, from_id, text, keyboard_markups.get_adding_interface_keyboard(
            handler.is_super_admin(from_id))):
        return admin_adding_interface, None

    if __compute_button_admin_delete_action(handler, from_id, text, keyboard_markups.get_deleting_interface_keyboard()):
        return admin_deletion_interface, None

    if __compute_button_show_results_table(handler, from_id, text):
        return default_admin_page, None

    if __compute_button_admin_get_list_of_exercises(handler, from_id, text):
        return default_admin_page, None

    if __compute_button_admin_get_list_of_accounts(handler, from_id, text):
        return default_admin_page, None

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_COMMAND)
    return default_admin_page, None


# Admin addition interface
def admin_adding_interface(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_back(handler, from_id, text, keyboard_markups.get_default_admin_keyboard()):
        return default_admin_page, None

    if handler.is_super_admin(from_id) and __compute_button_super_admin_add_admin_account(handler, from_id, text,
                                                                                          keyboard_markups.get_back_button_keyboard()):
        return adding_admin_waiting_login, None

    if __compute_button_admin_add_exercise(handler, from_id, text):
        return admin_adding_interface, None

    if __compute_button_admin_add_student(handler, from_id, text):
        return admin_adding_interface, None

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_COMMAND)
    return admin_adding_interface, None


# Adding exercise branch
def adding_exercise_waiting_exercise_name(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when admin wants to add new exercise (exercise_name)

    if __compute_button_back(handler, from_id, text,
                             keyboard_markups.get_adding_interface_keyboard(handler.is_super_admin(from_id)),
                             message_info=messages_text.MESSAGE_ON_ADMIN_ADD_COMMAND):
        return admin_adding_interface, None

    grade = int(data)  # Getting chooses grade
    exercise_name: str = text  # Current exercise name

    # If exercise with same name already exists, reset creating
    if handler.is_exists_exercise_name(exercise_name):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ALREADY_EXISTS_EXERCISE_NAME)
        return adding_exercise_waiting_exercise_name, data

    # If exercise name is incorrect, reset creating
    if exercise_name.count(inline_markups.CALLBACK_SEPARATION_ELEMENT) or not check_new_name(exercise_name):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_NEW_EXERCISE_NAME)
        return adding_exercise_waiting_exercise_name, data

    # If exercise name too long, reset creating
    if len(exercise_name) > constants.MAX_HOMEWORK_NAME_SIZE:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_TOO_LONG_NEW_EXERCISE_NAME)
        return adding_exercise_waiting_exercise_name, data

    # Start waiting number of tasks in new exercise
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_CORRECT_NEW_EXERCISE_NAME)
    return adding_exercise_waiting_number_of_right_answers, (grade, exercise_name)


def adding_exercise_waiting_number_of_right_answers(handler: UserHandler, from_id: int,
                                                    text: str, data) -> tuple[Callable, Any]:
    # This function is called on admin input during waiting number of tasks for create new exercise

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_back_button_keyboard(),
                             message_info=messages_text.MESSAGE_ON_START_WAITING_EXERCISE_NAME_FOR_CREATE):
        return adding_exercise_waiting_exercise_name, data[0]

    # Try to extract number of tasks from the message text
    success = True
    number_of_tasks = 0
    try:
        number_of_tasks = int(text)
    except:
        success = False

    # If number of tasks is incorrect or not positive, reset creating
    if not success or number_of_tasks <= 0:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_NUMBER_OF_TASKS)
        return adding_exercise_waiting_number_of_right_answers, data

    # Start waiting all right answers in new exercise
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_CORRECT_NUMBER_OF_TASKS)
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_MOVE_INTO_TASK_ADDING_INTERFACE.format(task_id=1),
                         markup=keyboard_markups.get_adding_exercise_interface_keyboard(1, number_of_tasks,
                                                                                        False, False, False))

    # Data description: (grade, exercise name, number of tasks, amount, list of right answers)
    return adding_exercise_task_settings_interface, {"exercise_grade": data[0], "exercise_name": data[1],
                                                    "number_tasks": number_of_tasks, "task_id": 1,
                                                    "right_answers": {1: []}, "task_statements": {},
                                                    "number_unchecked_tasks": number_of_tasks - 1}


def adding_exercise_task_settings_interface(handler: UserHandler, from_id: int,
                                            text: str, data) -> tuple[Callable, Any]:
    if __compute_button_back(handler, from_id, text, keyboard_markups.get_back_button_keyboard(),
                             message_info=messages_text.MESSAGE_ON_CORRECT_NEW_EXERCISE_NAME):
        return adding_exercise_waiting_number_of_right_answers, (data["exercise_grade"], data["exercise_name"])

    if __compute_button_adding_answer_for_task(handler, from_id, text, data, keyboard_markups.remove_keyboard()):
        return adding_exercise_waiting_answer_on_task, data

    if __compute_button_finish_creating_new_exercise(handler, from_id, text, data,
                                                     markup=keyboard_markups.get_adding_interface_keyboard(handler.is_super_admin(from_id))):
        return admin_adding_interface, None

    if __compute_button_adding_statement_for_task(handler, from_id, text, data,
                                                  markup=keyboard_markups.get_back_button_keyboard()):
        return adding_exercise_waiting_statement, data

    if __compute_button_go_to_previous_task_settings(handler, from_id, text, data):
        return adding_exercise_task_settings_interface, data

    if __compute_button_go_to_next_task_settings(handler, from_id, text, data):
        return adding_exercise_task_settings_interface, data

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_COMMAND)
    return adding_exercise_task_settings_interface, data


def adding_exercise_waiting_answer_on_task(handler: UserHandler, from_id: int,
                                           text: str, data) -> tuple[Callable, Any]:
    # This function is called on admin input during waiting of new right answer for create new exercise

    right_answer = text  # Current right answer

    if data["task_id"] not in data["right_answers"]:
        data["right_answers"][data["task_id"]] = []
        data["number_unchecked_tasks"] -= 1
    data["right_answers"][data["task_id"]].append(right_answer)

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ACCEPTED_RIGHT_ANSWER)
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_MOVE_INTO_TASK_ADDING_INTERFACE.format(task_id=data["task_id"]),
                         markup=keyboard_markups.get_adding_exercise_interface_keyboard(data["task_id"], data["number_tasks"],
                                                                                        data["task_id"] in data["right_answers"],
                                                                                        data["task_id"] in data["task_statements"],
                                                                                        data["number_unchecked_tasks"] == 0))
    return adding_exercise_task_settings_interface, data


def adding_exercise_waiting_statement(handler: UserHandler, from_id: int,
                                      text: str, data) -> tuple[Callable, Any]:
    # This function is called on admin input during waiting of task statement

    if __compute_button_back(handler, from_id, text,
                             keyboard_markups.get_adding_exercise_interface_keyboard(data["task_id"], data["number_tasks"],
                                                                                     data["task_id"] in data["right_answers"],
                                                                                     data["task_id"] in data["task_statements"],
                                                                                     data["number_unchecked_tasks"] == 0),
                             message_info=messages_text.MESSAGE_ON_MOVE_INTO_TASK_ADDING_INTERFACE.format(task_id=data["task_id"])):
        return adding_exercise_task_settings_interface, data

    text_statement = text
    statement_data = bytes()
    statement_ext = ""

    attachment = handler.current_user_attachment[from_id]
    if attachment is not None:
        statement_data = attachment.get_content()
        statement_ext = attachment.get_extension()

    data["task_statements"][data["task_id"]] = {"text_statement": text_statement, "statement_data": statement_data,
                                                "statement_ext": statement_ext}
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_SUCCESS_STATEMENT_ADDITION)
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_MOVE_INTO_TASK_ADDING_INTERFACE.format(task_id=data["task_id"]),
                         markup=keyboard_markups.get_adding_exercise_interface_keyboard(data["task_id"], data["number_tasks"],
                                                                                        data["task_id"] in data["right_answers"],
                                                                                        data["task_id"] in data["task_statements"],
                                                                                        data["number_unchecked_tasks"] == 0))
    return adding_exercise_task_settings_interface, data


# Adding student branch
def adding_student_waiting_login(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when admin wants to create new student account (waiting login)

    if __compute_button_back(handler, from_id, text,
                             keyboard_markups.get_adding_interface_keyboard(handler.is_super_admin(from_id)),
                             message_info=messages_text.MESSAGE_ON_ADMIN_ADD_COMMAND):
        return admin_adding_interface, None

    grade = int(data)  # Getting chooses grade
    login: str = text  # Current login

    # If login already exists, reset creating
    if handler.is_exists_login(login):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ALREADY_EXISTS_STUDENT_LOGIN)
        return adding_student_waiting_login, data

    # If login is incorrect, reset creating
    if login.count(inline_markups.CALLBACK_SEPARATION_ELEMENT) or not check_new_name(login):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_NEW_STUDENT_LOGIN)
        return adding_student_waiting_login, data

    # If login too long, reset creating
    if len(login) > constants.MAX_LOGIN_SIZE:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_TOO_LONG_NEW_STUDENT_LOGIN)
        return adding_student_waiting_login, data

    # Start waiting password of new student account
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_CORRECT_NEW_STUDENT_LOGIN)
    return adding_student_waiting_password, (grade, login)


def adding_student_waiting_password(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called on admin input during waiting password for create new student account

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_back_button_keyboard(),
                             message_info=messages_text.MESSAGE_ON_START_WAITING_LOGIN_OF_NEW_STUDENT_ACCOUNT):
        return adding_student_waiting_login, data[0]

    grade, login = int(data[0]), data[1]  # Getting chooses grade and current login
    password: str = text  # Current password

    handler.add_user(login, password, constants.STUDENT_STATUS, grade=grade)  # Creating new student account

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_SUCCESS_ADDING_NEW_STUDENT_ACCOUNT)
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_ADMIN_ADD_COMMAND,
                         markup=keyboard_markups.get_adding_interface_keyboard(handler.is_super_admin(from_id)))
    return admin_adding_interface, None


# Adding admin branch
def adding_admin_waiting_login(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when super-admin wants to create new admin account (waiting login)

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_adding_interface_keyboard(True),
                             message_info=messages_text.MESSAGE_ON_ADMIN_ADD_COMMAND):
        return admin_adding_interface, None

    login: str = text  # Current login

    # If login already exists, reset creating
    if handler.is_exists_login(login):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_ALREADY_EXISTS_ADMIN_LOGIN)
        return adding_admin_waiting_login, None

    # If login is incorrect, reset creating
    if login.count(inline_markups.CALLBACK_SEPARATION_ELEMENT) or not check_new_name(login):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_NEW_ADMIN_LOGIN)
        return adding_admin_waiting_login, None

    # If login too long, reset creating
    if len(login) > constants.MAX_LOGIN_SIZE:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_TOO_LONG_NEW_ADMIN_LOGIN)
        return adding_admin_waiting_login, None

    # Start waiting password of new admin account
    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_CORRECT_NEW_ADMIN_LOGIN)
    return adding_admin_waiting_password, login


def adding_admin_waiting_password(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when super-admin wants to create new admin account (waiting password)

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_back_button_keyboard(),
                             message_info=messages_text.MESSAGE_ON_SUPER_ADMIN_ADD_NEW_ADMIN):
        return adding_admin_waiting_login, None

    login: str = data  # Current login
    password: str = text  # Current password

    handler.add_user(login, password, constants.ADMIN_STATUS)  # Creating new admin account

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_SUCCESS_ADDING_NEW_ADMIN_ACCOUNT)
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_ADMIN_ADD_COMMAND,
                         markup=keyboard_markups.get_adding_interface_keyboard(handler.is_super_admin(from_id)))
    return admin_adding_interface, None


# Admin deletion interface
def admin_deletion_interface(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_back(handler, from_id, text, keyboard_markups.get_default_admin_keyboard()):
        return default_admin_page, None

    if __compute_button_admin_delete_account(handler, from_id, text, keyboard_markups.get_back_button_keyboard()):
        return deleting_account_waiting_login, None

    if __compute_button_admin_delete_exercise(handler, from_id, text, keyboard_markups.get_back_button_keyboard()):
        return deleting_exercise_waiting_name, None

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_UNKNOWN_COMMAND)
    return admin_deletion_interface, None


# Deleting account branch
def deleting_account_waiting_login(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when admin wants to delete exist account (waiting login)

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_deleting_interface_keyboard(),
                             message_info=messages_text.MESSAGE_ON_ADMIN_DELETE_COMMAND):
        return admin_deletion_interface, None

    login: str = text  # Current login
    user = handler.get_user_info_by_login(login)

    # If there is no such login, reset deleting
    if user is None:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_LOGIN_FOR_DELETE)
        return deleting_account_waiting_login, None

    # Admin can delete only users accounts
    if user.status == constants.SUPER_ADMIN_STATUS or not handler.is_super_admin(from_id) \
            and user.status == constants.ADMIN_STATUS:
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_FORBIDDEN_LOGIN_FOR_DELETE,
                             markup=keyboard_markups.get_deleting_interface_keyboard())
        return admin_deletion_interface, None

    # Send notification to last user if he exists
    if user.telegram_id != constants.UNAUTHORIZED_TELEGRAM_ID:
        handler.send_message(send_id=user.telegram_id, text=messages_text.NOTIFICATION_FOR_LAST_USER_ON_DELETED_ACCOUNT,
                             markup=keyboard_markups.remove_keyboard())
        handler.update_user_state(user.telegram_id, unauthorized_user_waiting_login, None)

    handler.delete_user(login)  # Deleting account

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_SUCCESS_DELETION_ACCOUNT)
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_ADMIN_DELETE_COMMAND,
                         markup=keyboard_markups.get_deleting_interface_keyboard())
    return admin_deletion_interface, None


# Deleting exercise branch
def deleting_exercise_waiting_name(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when admin wants to delete exist exercise (waiting homework name)

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_deleting_interface_keyboard(),
                             message_info=messages_text.MESSAGE_ON_ADMIN_DELETE_COMMAND):
        return admin_deletion_interface, None

    exercise_name: str = text  # Current exercise name

    # If there is no such exercise, reset deleting
    if not handler.is_exists_exercise_name(exercise_name):
        handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_INVALID_EXERCISE_NAME_FOR_DELETE)
        return deleting_exercise_waiting_name, None

    handler.delete_exercise(exercise_name)  # Deleting exercise

    handler.send_message(send_id=from_id, text=messages_text.MESSAGE_ON_SUCCESS_DELETION_EXERCISE)
    handler.send_message(send_id=from_id,
                         text=messages_text.MESSAGE_ON_ADMIN_DELETE_COMMAND,
                         markup=keyboard_markups.get_deleting_interface_keyboard())
    return admin_deletion_interface, None
