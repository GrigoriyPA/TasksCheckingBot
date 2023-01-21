from telebot import types

# Common:
BUTTON_SHOW_RESULTS_TABLE = "Вывести результаты"  # Show results table
BUTTON_SHOW_STATUS = "Статус"  # Get login, password and status of current account
BUTTON_EXIT = "Выйти"  # Exit from current account

# Students
BUTTON_SOLVE_EXERCISE = "Сдать задачу"  # Solve unsolved exercise

# Admins:
BUTTON_ADD = "Добавить"  # Button for select add action type (admin/super-admin)
BUTTON_DELETE = "Удалить"  # Button for select delete action type (admin/super-admin)
BUTTON_ACCOUNTS_LIST = "Список аккаунтов"  # Show accounts list (admin/super-admin)
BUTTON_EXERCISES_LIST = "Список заданий"  # Show exercises list (admin/super-admin)


def get_default_admin_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Buttons description on bottom bar
    markup.add(types.KeyboardButton(text=BUTTON_ACCOUNTS_LIST),
               types.KeyboardButton(text=BUTTON_EXERCISES_LIST),
               types.KeyboardButton(text=BUTTON_SHOW_RESULTS_TABLE))
    markup.add(types.KeyboardButton(text=BUTTON_ADD),
               types.KeyboardButton(text=BUTTON_DELETE))
    markup.add(types.KeyboardButton(text=BUTTON_SHOW_STATUS))
    markup.add(types.KeyboardButton(text=BUTTON_EXIT))
    return markup


def get_default_student_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Buttons description on bottom bar
    markup.add(types.KeyboardButton(text=BUTTON_SOLVE_EXERCISE),
               types.KeyboardButton(text=BUTTON_SHOW_RESULTS_TABLE))
    markup.add(types.KeyboardButton(text=BUTTON_SHOW_STATUS))
    markup.add(types.KeyboardButton(text=BUTTON_EXIT))
    return markup
