from telebot import types

# Common:
BUTTON_SHOW_RESULTS_TABLE = "Вывести результаты"  # Show results table
BUTTON_SHOW_STATUS = "Статус"  # Get login, password and status of current account
BUTTON_EXIT = "Выйти"  # Exit from current account
BUTTON_BACK = "Назад"  # Go to last state

# Students
BUTTON_SOLVE_EXERCISE = "Сдать задачу"  # Solve unsolved exercise

# Admins:
BUTTON_ADD = "Добавить"  # Button for select add action type (admin/super-admin)
BUTTON_DELETE = "Удалить"  # Button for select delete action type (admin/super-admin)
BUTTON_ACCOUNTS_LIST = "Список аккаунтов"  # Show accounts list (admin/super-admin)
BUTTON_EXERCISES_LIST = "Список заданий"  # Show exercises list (admin/super-admin)
BUTTON_ADD_STUDENT = "Ученик"  # Add new student account
BUTTON_ADD_ADMIN = "Администратор"  # Add new admin account
BUTTON_ADD_EXERCISE = "Задание"  # Add new admin exercise


def remove_keyboard() -> types.ReplyKeyboardRemove:
    return types.ReplyKeyboardRemove()


def get_back_button_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=BUTTON_BACK))
    return markup


def get_default_admin_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=BUTTON_ACCOUNTS_LIST),
               types.KeyboardButton(text=BUTTON_EXERCISES_LIST),
               types.KeyboardButton(text=BUTTON_SHOW_RESULTS_TABLE))
    markup.add(types.KeyboardButton(text=BUTTON_ADD),
               types.KeyboardButton(text=BUTTON_DELETE))
    markup.add(types.KeyboardButton(text=BUTTON_SHOW_STATUS))
    markup.add(types.KeyboardButton(text=BUTTON_EXIT))
    return markup


def get_addition_interface_keyboard(is_super_admin: bool) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=BUTTON_ADD_STUDENT))
    if is_super_admin:
        markup.add(types.KeyboardButton(text=BUTTON_ADD_ADMIN))
    markup.add(types.KeyboardButton(text=BUTTON_ADD_EXERCISE))
    markup.add(types.KeyboardButton(text=BUTTON_BACK))
    return markup


def get_default_student_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=BUTTON_SOLVE_EXERCISE),
               types.KeyboardButton(text=BUTTON_SHOW_RESULTS_TABLE))
    markup.add(types.KeyboardButton(text=BUTTON_SHOW_STATUS))
    markup.add(types.KeyboardButton(text=BUTTON_EXIT))
    return markup
