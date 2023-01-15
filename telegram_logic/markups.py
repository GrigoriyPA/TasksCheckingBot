from telebot import types
import constants


def get_homework_list(homework_list, check_name):
    keyboard = []
    row = []
    id = 0
    for name in homework_list:
        if not check_name(name):
            continue

        row.append(types.InlineKeyboardButton(text=name, callback_data="SELECT_HOMEWORK " + name))
        if len(row) == constants.HOMEWORKS_NUMBER_IN_LINE:
            keyboard.append(row)
            row = []

        id += 1

    if len(row) > 0:
        keyboard.append(row)

    return types.InlineKeyboardMarkup(keyboard)


def get_task_list(homework_size, homework_name, check_task):
    keyboard = []
    row = []
    id = 0
    for task_id in range(1, homework_size + 1):
        if not check_task(homework_name, task_id):
            continue

        row.append(types.InlineKeyboardButton(text=str(task_id), callback_data="SELECT_TASK " + homework_name + " " + str(task_id)))
        if len(row) == constants.TASKS_NUMBER_IN_LINE:
            keyboard.append(row)
            row = []

        id += 1

    if len(row) > 0:
        keyboard.append(row)
        row = []

    return types.InlineKeyboardMarkup(keyboard)
