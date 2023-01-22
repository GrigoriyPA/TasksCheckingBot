from bot import constants
from bot.telegram_logic import inline_markups
from bot.telegram_logic import keyboard_markups
from bot.telegram_logic.user_handler import UserHandler, check_new_login, MARKUP_TYPES
from typing import Any, Callable

# __compute_button_back
MESSAGE_ON_EXIT_FROM_CURRENT_STATE = "Отмена...\n"

# __compute_button_exit
MESSAGE_ON_LOG_OUT_FROM_CURRENT_ACCOUNT = "Вы вышли из текущего аккаунта.\n"

# __compute_button_status
MESSAGE_ON_STATUS_UNAUTHORIZED_ACCOUNT = "Статус: не авторизован"
MESSAGE_ON_STATUS_ADMIN_ACCOUNT = "Логин: {login}\nПароль: {password}\nСтатус: {status}"
MESSAGE_ON_STATUS_STUDENT_ACCOUNT = "Логин: {login}\nПароль: {password}\nСтатус: {status}\nКласс: {grade}"

# __compute_button_show_results_table
MESSAGE_ON_COMMAND_SHOW_RESULTS_TABLE_NO_HOMEWORKS_OPENED = "На данный момент нет открытых работ."
MESSAGE_ON_COMMAND_SHOW_RESULTS_TABLE = "Веберите имя работы."

# __compute_button_admin_get_list_of_exercises
MESSAGE_ON_GET_LIST_OF_EXERCISES_NO_HOMEWORKS_OPENED = "На данный момент нет открытых работ."

# __compute_button_admin_get_list_of_accounts
TOP_MESSAGE_OF_LIST_OF_SUPER_ADMINS = "Супер-администраторы:"
TOP_MESSAGE_OF_LIST_OF_ADMINS = "Администраторы:"
TOP_MESSAGE_OF_LIST_OF_STUDENTS = "Ученики:"
STUDENT_DESCRIPTION_IN_LIST_OF_STUDENTS = "{login}, {grade} класс"

# __compute_button_admin_add_action
MESSAGE_ON_ADMIN_ADD_COMMAND = "Выберите объект для добавления:"

# __compute_button_admin_delete_action
MESSAGE_ON_ADMIN_DELETE_COMMAND = "Выберите объект для удаления:"

# __compute_button_student_send_answer
MESSAGE_ON_STUDENT_SEND_ANSWER_NO_HOMEWORKS_AVAILABLE = "На данный момент для вас нет открытых работ."
MESSAGE_ON_STUDENT_SEND_ANSWER = "Веберите имя работы."

CALLBACK_DATA_SELECT_HOMEWORK_FOR_SEND_ANSWER = "A"

# __compute_button_admin_add_student
MESSAGE_ON_ADMIN_ADD_NEW_STUDENT = "Выберите класс нового ученика."

CALLBACK_DATA_SELECT_STUDENT_GRADE_FOR_CREATE = "M"

# __compute_button_admin_add_exercise
MESSAGE_ON_ADMIN_ADD_NEW_EXERCISE = "Выберите для какого класса будет создано задание."

CALLBACK_DATA_SELECT_EXERCISE_GRADE_FOR_CREATE = "N"

# __compute_button_super_admin_add_admin_account
MESSAGE_ON_SUPER_ADMIN_ADD_NEW_ADMIN = "Введите логин для нового аккаунта администратора."

# __compute_button_admin_delete_account
MESSAGE_ON_ADMIN_DELETE_ACCOUNT = "Введите логин аккаунта для удаления:"

# __compute_button_admin_delete_exercise
MESSAGE_ON_ADMIN_DELETE_EXERCISE = "Введите название работы для удаления:"

# common
MESSAGE_ON_UNKNOWN_COMMAND = "Неизвестная команда."

# default_state
WELCOME_MESSAGE_FOR_ADMIN = "С возвращением. Статус аккаунта: администратор."
WELCOME_MESSAGE_FOR_STUDENT = "С возвращением. Статус аккаунта: ученик."
WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS = "Введите логин аккаунта для авторизации:"

# unauthorized_user_waiting_login
MESSAGE_ON_INVALID_LOGIN = "Введённый логин не существует, повторите попытку."
MESSAGE_ON_VALID_LOGIN = "Введите пароль:"

# unauthorized_user_waiting_password
MESSAGE_ON_INVALID_PASSWORD = "Введён неправильный пароль, повторите попытку."
NOTIFICATION_FOR_LAST_USER_ON_AUTHORIZED_ACCOUNT = "В ваш профиль выполнен вход с другого телеграм аккаунта, " \
                                                   "вы были разлогинены. Введите логин для авторизации."
MESSAGE_ON_SUCCESS_ADMIN_AUTHORIZATION = "Успешная авторизация. Статус аккаунта: администратор."
MESSAGE_ON_SUCCESS_STUDENT_AUTHORIZATION = "Успешная авторизация. Статус аккаунта: ученик."

# adding_admin_waiting_login
MESSAGE_ON_ALREADY_EXISTS_ADMIN_LOGIN = "Введённый логин уже существует, повторите попытку."
MESSAGE_ON_INVALID_NEW_ADMIN_LOGIN = "Введённый логин содержит запрещённые символы, повторите попытку."
MESSAGE_ON_TOO_LONG_NEW_ADMIN_LOGIN = "Введённый логин слишком длинный, повторите попытку."
MESSAGE_ON_CORRECT_NEW_ADMIN_LOGIN = "Введите пароль для нового аккаунта администратора:"

# adding_admin_waiting_password
MESSAGE_ON_SUCCESS_ADDING_NEW_ADMIN_ACCOUNT = "Новый аккаунт администратора успешно создан."

# deleting_account_waiting_login
MESSAGE_ON_INVALID_LOGIN_FOR_DELETE = "Введённый логин не существует, повторите попытку."
MESSAGE_ON_FORBIDDEN_LOGIN_FOR_DELETE = "Вы не можете удалить этот аккаунт."
NOTIFICATION_FOR_LAST_USER_ON_DELETED_ACCOUNT = "Ваш аккаунт был удалён администратором. Введите логин для авторизации."
MESSAGE_ON_SUCCESS_DELETION_ACCOUNT = "Аккаунт успешно удалён."

# deleting_exercise_waiting_name
MESSAGE_ON_INVALID_EXERCISE_NAME_FOR_DELETE = "Не существует работы с введённым именем, повторите попытку."
MESSAGE_ON_SUCCESS_DELETION_EXERCISE = "Работа успешно удалена."


# Special computing functions

# Checking back button (common interface)
def __compute_button_back(handler: UserHandler, from_id: int, text: str, markup: MARKUP_TYPES = None,
                          message_info: str = '') -> bool:
    if text != keyboard_markups.BUTTON_BACK:
        # There is no back button pressed
        return False

    # Back button have pressed, go back from current state
    handler.send_message(send_id=from_id, text=MESSAGE_ON_EXIT_FROM_CURRENT_STATE + message_info, markup=markup)
    return True


# Checking exit button (common interface)
def __compute_button_exit(handler: UserHandler, from_id: int, text: str, markup: MARKUP_TYPES = None,
                          message_info: str = '') -> bool:
    if text != keyboard_markups.BUTTON_EXIT:
        # There is no exit button pressed
        return False

    # Exit button have pressed, exit from current account
    handler.sign_out_user(from_id)
    handler.send_message(send_id=from_id, text=MESSAGE_ON_LOG_OUT_FROM_CURRENT_ACCOUNT + message_info, markup=markup)
    return True


# Checking status button (common interface)
def __compute_button_status(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != keyboard_markups.BUTTON_SHOW_STATUS:
        # There is no exit button pressed
        return False

    # Status button have pressed, show status of current account
    user_info = handler.get_user_info_by_id(from_id)
    if user_info is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_STATUS_UNAUTHORIZED_ACCOUNT)
    elif user_info.status == constants.STUDENT_STATUS:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_STATUS_STUDENT_ACCOUNT.format(login=user_info.login,
                                                                                            password=user_info.password,
                                                                                            status=user_info.status,
                                                                                            grade=user_info.grade))
    else:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_STATUS_ADMIN_ACCOUNT.format(login=user_info.login,
                                                                                          password=user_info.password,
                                                                                          status=user_info.status))
    return True


# Checking show results table button (common interface)
def __compute_button_show_results_table(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != keyboard_markups.BUTTON_SHOW_RESULTS_TABLE:
        # There is no show results table button pressed
        return False

    # Create list of exists homeworks
    markup = inline_markups.get_list_of_all_homeworks_inline_markup(handler.get_all_exercises_names(),
                                                                    inline_markups.CALLBACK_DATA_SHOW_RESULTS_TABLE)
    if markup is None:
        # There is no opened homeworks
        handler.send_message(send_id=from_id, text=MESSAGE_ON_COMMAND_SHOW_RESULTS_TABLE_NO_HOMEWORKS_OPENED)
    else:
        # Print list of exists homework
        handler.send_message(send_id=from_id, text=MESSAGE_ON_COMMAND_SHOW_RESULTS_TABLE, markup=markup)
    return True


# Checking admin get list of exercises button (default admin interface)
def __compute_button_admin_get_list_of_exercises(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != keyboard_markups.BUTTON_EXERCISES_LIST:
        # There is no admin get list of exercises button pressed
        return False

    # Admin get list of exercises button have pressed, print list of exists exercises
    exercises_names = handler.get_all_exercises_names()
    exercises_names.sort()

    if len(exercises_names) == 0:
        # There is no homeworks created
        handler.send_message(send_id=from_id, text=MESSAGE_ON_GET_LIST_OF_EXERCISES_NO_HOMEWORKS_OPENED)
        return True

    # Send list of homeworks
    for name in exercises_names:
        handler.send_message(send_id=from_id, text=name, markup=inline_markups.get_exercise_actions_inline_markup(name))
    return True


# Checking admin get list of accounts button (default admin interface)
def __compute_button_admin_get_list_of_accounts(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != keyboard_markups.BUTTON_ACCOUNTS_LIST:
        # There is no admin get list of accounts button pressed
        return False

    # Admin get list of accounts button have pressed, print list of exists accounts

    # Admins can see only other admins and users (not super-admins)
    if handler.is_super_admin(from_id):
        users = handler.get_users_info_by_status(constants.SUPER_ADMIN_STATUS)
        users.sort(key=lambda current_user: current_user.login)
        if len(users) > 0:
            # Send list of super-admins
            handler.send_message(send_id=from_id, text=TOP_MESSAGE_OF_LIST_OF_SUPER_ADMINS)
            for user in users:
                handler.send_message(send_id=from_id, text=user.login,
                                     markup=inline_markups.get_admin_account_actions_inline_markup(user.login))

    users = handler.get_users_info_by_status(constants.ADMIN_STATUS)
    users.sort(key=lambda current_user: current_user.login)
    if len(users) > 0:
        # Send list of admins
        handler.send_message(send_id=from_id, text=TOP_MESSAGE_OF_LIST_OF_ADMINS)
        for user in users:
            handler.send_message(send_id=from_id, text=user.login,
                                 markup=inline_markups.get_admin_account_actions_inline_markup(user.login))

    users = handler.get_users_info_by_status(constants.STUDENT_STATUS)
    users.sort(key=lambda current_user: current_user.login)
    if len(users) > 0:
        # Send list of students
        handler.send_message(send_id=from_id, text=TOP_MESSAGE_OF_LIST_OF_STUDENTS)
        for user in users:
            handler.send_message(send_id=from_id,
                                 text=STUDENT_DESCRIPTION_IN_LIST_OF_STUDENTS.format(login=user.login,
                                                                                     grade=str(user.grade)),
                                 markup=inline_markups.get_student_account_actions_inline_markup(user.login))
    return True


# Checking admin add action button (default admin interface)
def __compute_button_admin_add_action(handler: UserHandler, from_id: int, text: str,
                                      markup: MARKUP_TYPES = None) -> bool:
    if text != keyboard_markups.BUTTON_ADD:
        # There is no admin add action button pressed
        return False

    # Admin add action button have pressed, update state and keyboard
    handler.send_message(send_id=from_id, text=MESSAGE_ON_ADMIN_ADD_COMMAND, markup=markup)
    return True


# Checking admin delete action button (default admin interface)
def __compute_button_admin_delete_action(handler: UserHandler, from_id: int, text: str,
                                         markup: MARKUP_TYPES = None) -> bool:
    if text != keyboard_markups.BUTTON_DELETE:
        # There is no admin delete action button pressed
        return False

    # Admin delete action button have pressed, update state and keyboard
    handler.send_message(send_id=from_id, text=MESSAGE_ON_ADMIN_DELETE_COMMAND, markup=markup)
    return True


# Checking student send answer button (default student interface)
def __compute_button_student_send_answer(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != keyboard_markups.BUTTON_SOLVE_EXERCISE:
        # There is no student send answer button pressed
        return False

    user_info = handler.get_user_info_by_id(from_id)

    # Create list of available homeworks
    if user_info is not None:
        markup = inline_markups.get_list_of_all_homeworks_inline_markup(
            handler.get_all_exercises_names_for_grade(user_info.grade),
            CALLBACK_DATA_SELECT_HOMEWORK_FOR_SEND_ANSWER)
    else:
        markup = None

    # Student send answer button have pressed, print list of available exercises
    if markup is None:
        # There is no available homeworks
        handler.send_message(send_id=from_id, text=MESSAGE_ON_STUDENT_SEND_ANSWER_NO_HOMEWORKS_AVAILABLE)
    else:
        # Print list of exists homework
        handler.send_message(send_id=from_id, text=MESSAGE_ON_STUDENT_SEND_ANSWER, markup=markup)
    return True


# Checking admin add student button (adding admin interface)
def __compute_button_admin_add_student(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != keyboard_markups.BUTTON_ADD_STUDENT:
        # There is no admin add student button pressed
        return False

    # Admin add student button have pressed, print list of all grades
    handler.send_message(send_id=from_id, text=MESSAGE_ON_ADMIN_ADD_NEW_STUDENT,
                         markup=inline_markups.get_list_of_all_grades_inline_markup(
                             CALLBACK_DATA_SELECT_STUDENT_GRADE_FOR_CREATE))
    return True


# Checking admin add exercise button (adding admin interface)
def __compute_button_admin_add_exercise(handler: UserHandler, from_id: int, text: str) -> bool:
    if text != keyboard_markups.BUTTON_ADD_EXERCISE:
        # There is no admin add exercise button pressed
        return False

    # Admin add exercise button have pressed, print list of all grades
    handler.send_message(send_id=from_id, text=MESSAGE_ON_ADMIN_ADD_NEW_EXERCISE,
                         markup=inline_markups.get_list_of_all_grades_inline_markup(
                             CALLBACK_DATA_SELECT_EXERCISE_GRADE_FOR_CREATE))
    return True


# Checking super-admin add admin account button (adding super-admin interface)
def __compute_button_super_admin_add_admin_account(handler: UserHandler, from_id: int, text: str,
                                                   markup: MARKUP_TYPES = None) -> bool:
    if text != keyboard_markups.BUTTON_ADD_ADMIN:
        # There is no super-admin add admin account button pressed
        return False

    # Super-admin add admin account button have pressed, start waiting login of new account
    handler.send_message(send_id=from_id, text=MESSAGE_ON_SUPER_ADMIN_ADD_NEW_ADMIN, markup=markup)
    return True


# Checking admin delete account button (deleting admin interface)
def __compute_button_admin_delete_account(handler: UserHandler, from_id: int, text: str,
                                          markup: MARKUP_TYPES = None) -> bool:
    if text != keyboard_markups.BUTTON_DELETE_ACCOUNT:
        # There is no admin delete account button pressed
        return False

    # Admin delete account button have pressed, start waiting login of deletion account
    handler.send_message(send_id=from_id, text=MESSAGE_ON_ADMIN_DELETE_ACCOUNT, markup=markup)
    return True


# Checking admin delete exercise button (deleting admin interface)
def __compute_button_admin_delete_exercise(handler: UserHandler, from_id: int, text: str,
                                           markup: MARKUP_TYPES = None) -> bool:
    if text != keyboard_markups.BUTTON_DELETE_EXERCISE:
        # There is no admin delete exercise button pressed
        return False

    # Admin delete exercise button have pressed, start waiting name of deletion exercise
    handler.send_message(send_id=from_id, text=MESSAGE_ON_ADMIN_DELETE_EXERCISE, markup=markup)
    return True


# Bot state functions

# Initial state
def default_state(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called on first user message to bot (in current session)

    if handler.is_admin(from_id):
        # Current user is admin, go to admin home page
        handler.send_message(send_id=from_id, text=WELCOME_MESSAGE_FOR_ADMIN,
                             markup=keyboard_markups.get_default_admin_keyboard())
        return default_admin_page, None

    if handler.is_student(from_id):
        # Current user is student, go to student home page
        handler.send_message(send_id=from_id, text=WELCOME_MESSAGE_FOR_STUDENT,
                             markup=keyboard_markups.get_default_student_keyboard())
        return default_student_page, None

    # Current user is unauthorized, start waiting of login for authorization
    handler.send_message(send_id=from_id, text=WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS,
                         markup=keyboard_markups.remove_keyboard())
    return unauthorized_user_waiting_login, None


# Authorization branch
def unauthorized_user_waiting_login(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when user wants to authorize (waiting login)

    login: str = text  # Current login

    # If there is no such login, reset authorization
    if not handler.is_exists_login(login):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_INVALID_LOGIN)
        return unauthorized_user_waiting_login, None

    # Start waiting of password for authorizing in current login
    handler.send_message(send_id=from_id, text=MESSAGE_ON_VALID_LOGIN,
                         markup=keyboard_markups.get_back_button_keyboard())
    return unauthorized_user_waiting_password, login


def unauthorized_user_waiting_password(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when user wants to authorize (waiting password, login stored in data)

    if __compute_button_back(handler, from_id, text, keyboard_markups.remove_keyboard(),
                             message_info=WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS):
        return unauthorized_user_waiting_login, None

    login: str = data  # Current login
    password: str = text  # Current password

    # If password is incorrect, reset authorization
    if not handler.is_valid_password(login, password):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_INVALID_PASSWORD)
        return unauthorized_user_waiting_password, login

    user = handler.get_user_info_by_login(login)

    # Send notification for last user on current login, if he exists
    if user.telegram_id != constants.UNAUTHORIZED_TELEGRAM_ID:
        handler.send_message(send_id=user.telegram_id, text=NOTIFICATION_FOR_LAST_USER_ON_AUTHORIZED_ACCOUNT,
                             markup=keyboard_markups.remove_keyboard())
        handler.update_user_state(user.telegram_id, unauthorized_user_waiting_login, None)

    handler.sign_in_user(login, from_id)  # Authorize current user

    if handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_SUCCESS_ADMIN_AUTHORIZATION,
                             markup=keyboard_markups.get_default_admin_keyboard())
        return default_admin_page, None

    handler.send_message(send_id=from_id, text=MESSAGE_ON_SUCCESS_STUDENT_AUTHORIZATION,
                         markup=keyboard_markups.get_default_student_keyboard())
    return default_student_page, None


# Initial student interface
def default_student_page(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_exit(handler, from_id, text, keyboard_markups.remove_keyboard(),
                             message_info=WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS):
        return unauthorized_user_waiting_login, None

    if __compute_button_status(handler, from_id, text):
        return default_student_page, None

    if __compute_button_show_results_table(handler, from_id, text):
        return default_student_page, None

    if __compute_button_student_send_answer(handler, from_id, text):
        return default_student_page, None

    handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_COMMAND)
    return default_student_page, None


# Initial admin interface
def default_admin_page(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_exit(handler, from_id, text, keyboard_markups.remove_keyboard(),
                             message_info=WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS):
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

    handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_COMMAND)
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

    handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_COMMAND)
    return admin_adding_interface, None


# Adding admin branch
def adding_admin_waiting_login(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when super-admin wants to create new admin account (waiting login)

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_adding_interface_keyboard(True),
                             message_info=MESSAGE_ON_ADMIN_ADD_COMMAND):
        return admin_adding_interface, None

    login: str = text  # Current login

    # If login already exists, stop creating, reset creating
    if handler.is_exists_login(login):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_ALREADY_EXISTS_ADMIN_LOGIN)
        return adding_admin_waiting_login, None

    # If login is incorrect, reset creating
    if login.count(inline_markups.CALLBACK_SEPARATION_ELEMENT) or not check_new_login(login):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_INVALID_NEW_ADMIN_LOGIN)
        return adding_admin_waiting_login, None

    # If login too long, reset creating
    if len(login) > constants.MAX_LOGIN_SIZE:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_TOO_LONG_NEW_ADMIN_LOGIN)
        return adding_admin_waiting_login, None

    # Start waiting password of new account
    handler.send_message(send_id=from_id, text=MESSAGE_ON_CORRECT_NEW_ADMIN_LOGIN)
    return adding_admin_waiting_password, login


def adding_admin_waiting_password(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when super-admin wants to create new admin account (waiting password)

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_back_button_keyboard(),
                             message_info=MESSAGE_ON_SUPER_ADMIN_ADD_NEW_ADMIN):
        return adding_admin_waiting_login, None

    login: str = data  # Current login
    password: str = text  # Current password

    handler.add_user(login, password, constants.ADMIN_STATUS)  # Creating new admin account

    handler.send_message(send_id=from_id, text=MESSAGE_ON_SUCCESS_ADDING_NEW_ADMIN_ACCOUNT,
                         markup=keyboard_markups.get_adding_interface_keyboard(True))
    return admin_adding_interface, None


# Admin deletion interface
def admin_deletion_interface(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_back(handler, from_id, text, keyboard_markups.get_default_admin_keyboard()):
        return default_admin_page, None

    if __compute_button_admin_delete_account(handler, from_id, text, keyboard_markups.get_back_button_keyboard()):
        return deleting_account_waiting_login, None

    if __compute_button_admin_delete_exercise(handler, from_id, text, keyboard_markups.get_back_button_keyboard()):
        return deleting_exercise_waiting_name, None

    handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_COMMAND)
    return admin_deletion_interface, None


# Deleting account branch
def deleting_account_waiting_login(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when admin wants to delete exist account (waiting login)

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_deleting_interface_keyboard(),
                             message_info=MESSAGE_ON_ADMIN_DELETE_COMMAND):
        return admin_deletion_interface, None

    login: str = text  # Current login
    user = handler.get_user_info_by_login(login)

    # If there is no such login, reset deleting
    if user is None:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_INVALID_LOGIN_FOR_DELETE)
        return deleting_account_waiting_login, None

    # Admin can delete only users accounts
    if user.status == constants.SUPER_ADMIN_STATUS or not handler.is_super_admin(from_id) \
            and user.status == constants.ADMIN_STATUS:
        handler.send_message(send_id=from_id, text=MESSAGE_ON_FORBIDDEN_LOGIN_FOR_DELETE,
                             markup=keyboard_markups.get_deleting_interface_keyboard())
        return admin_deletion_interface, None

    # Send notification to last user if he exists
    if user.telegram_id != constants.UNAUTHORIZED_TELEGRAM_ID:
        handler.send_message(send_id=user.telegram_id, text=NOTIFICATION_FOR_LAST_USER_ON_DELETED_ACCOUNT,
                             markup=keyboard_markups.remove_keyboard())
        handler.update_user_state(user.telegram_id, unauthorized_user_waiting_login, None)

    handler.delete_user(login)  # Deleting account

    handler.send_message(send_id=from_id, text=MESSAGE_ON_SUCCESS_DELETION_ACCOUNT,
                         markup=keyboard_markups.get_deleting_interface_keyboard())
    return admin_deletion_interface, None


# Deleting exercise branch
def deleting_exercise_waiting_name(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    # This function is called when admin wants to delete exist exercise (waiting homework name)

    if __compute_button_back(handler, from_id, text, keyboard_markups.get_deleting_interface_keyboard(),
                             message_info=MESSAGE_ON_ADMIN_DELETE_COMMAND):
        return admin_deletion_interface, None

    exercise_name: str = text  # Current exercise name

    # If there is no such exercise, reset deleting
    if not handler.is_exists_exercise_name(exercise_name):
        handler.send_message(send_id=from_id, text=MESSAGE_ON_INVALID_EXERCISE_NAME_FOR_DELETE)
        return deleting_exercise_waiting_name, None

    handler.delete_exercise(exercise_name)  # Deleting exercise

    handler.send_message(send_id=from_id, text=MESSAGE_ON_SUCCESS_DELETION_EXERCISE,
                         markup=keyboard_markups.get_deleting_interface_keyboard())
    return admin_deletion_interface, None
