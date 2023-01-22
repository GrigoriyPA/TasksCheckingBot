from bot import constants
from bot.telegram_logic import keyboard_markups
from bot.telegram_logic.user_handler import UserHandler, MARKUP_TYPES
from typing import Any, Callable

# __compute_button_back
MESSAGE_ON_EXIT_FROM_CURRENT_STATE = "Отмена...\n"

# __compute_button_exit
MESSAGE_ON_LOG_OUT_FROM_CURRENT_ACCOUNT = "Вы вышли из текущего аккаунта.\n"

# __compute_button_status
MESSAGE_ON_STATUS_UNAUTHORIZED_ACCOUNT = "Статус: не авторизован"
MESSAGE_ON_STATUS_ADMIN_ACCOUNT = "Логин: {login}\nПароль: {password}\nСтатус: {status}"
MESSAGE_ON_STATUS_STUDENT_ACCOUNT = "Логин: {login}\nПароль: {password}\nСтатус: {status}\nКласс: {grade}"

# __compute_button_admin_add_action
MESSAGE_ON_ADMIN_ADD_COMMAND = "Выберите объект для добавления:"

# __compute_button_admin_delete_action
MESSAGE_ON_ADMIN_DELETE_COMMAND = "Выберите объект для удаления:"

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


# Special computing functions

# Checking back button
def __compute_button_back(handler: UserHandler, from_id: int, text: str, markup: MARKUP_TYPES = None,
                          message_info: str = '') -> bool:
    if text != keyboard_markups.BUTTON_BACK:
        # There is no back button pressed
        return False

    # Back button have pressed, go back from current state
    handler.send_message(send_id=from_id, text=MESSAGE_ON_EXIT_FROM_CURRENT_STATE + message_info, markup=markup)
    return True


# Checking exit button
def __compute_button_exit(handler: UserHandler, from_id: int, text: str, markup: MARKUP_TYPES = None,
                          message_info: str = '') -> bool:
    if text != keyboard_markups.BUTTON_EXIT:
        # There is no exit button pressed
        return False

    # Exit button have pressed, exit from current account
    handler.sign_out_user(from_id)
    handler.send_message(send_id=from_id, text=MESSAGE_ON_LOG_OUT_FROM_CURRENT_ACCOUNT + message_info, markup=markup)
    return True


# Checking status button
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


# Checking admin add action button
def __compute_button_admin_add_action(handler: UserHandler, from_id: int, text: str,
                                      markup: MARKUP_TYPES = None) -> bool:
    if text != keyboard_markups.BUTTON_ADD:
        # There is no admin add action button pressed
        return False

    # Admin add action button have pressed, update state and keyboard
    handler.send_message(send_id=from_id, text=MESSAGE_ON_ADMIN_ADD_COMMAND, markup=markup)
    return True


# Checking admin delete action button
def __compute_button_admin_delete_action(handler: UserHandler, from_id: int, text: str,
                                         markup: MARKUP_TYPES = None) -> bool:
    if text != keyboard_markups.BUTTON_DELETE:
        # There is no admin delete action button pressed
        return False

    # Admin delete action button have pressed, update state and keyboard
    handler.send_message(send_id=from_id, text=MESSAGE_ON_ADMIN_DELETE_COMMAND, markup=markup)
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
    if not handler.is_valid_login(login):
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


# Initial student state
def default_student_page(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_exit(handler, from_id, text, keyboard_markups.remove_keyboard(),
                             message_info=WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS):
        return unauthorized_user_waiting_login, None

    if __compute_button_status(handler, from_id, text):
        return default_student_page, None

    handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_COMMAND)
    return default_student_page, None


# Initial admin state
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

    handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_COMMAND)
    return default_admin_page, None


# Admin addition interface
def admin_adding_interface(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_back(handler, from_id, text, keyboard_markups.get_default_admin_keyboard()):
        return default_admin_page, None

    handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_COMMAND)
    return admin_adding_interface, None


# Admin deletion interface
def admin_deletion_interface(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if __compute_button_back(handler, from_id, text, keyboard_markups.get_default_admin_keyboard()):
        return default_admin_page, None

    handler.send_message(send_id=from_id, text=MESSAGE_ON_UNKNOWN_COMMAND)
    return admin_deletion_interface, None
