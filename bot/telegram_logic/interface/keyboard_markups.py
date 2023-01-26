from bot.telegram_logic.interface import messages_text
from telebot import types


def remove_keyboard() -> types.ReplyKeyboardRemove:
    return types.ReplyKeyboardRemove()


def get_back_button_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_BACK))
    return markup


def get_default_student_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_SOLVE_EXERCISE),
               types.KeyboardButton(text=messages_text.BUTTON_SHOW_RESULTS_TABLE))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_SHOW_STATUS))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_EXIT))
    return markup


def get_student_send_explanation_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_STUDENT_WANT_TO_SEND_EXPLANATION))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_STUDENT_DO_NOT_WANT_TO_SEND_EXPLANATION))
    return markup


def get_default_admin_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_ACCOUNTS_LIST),
               types.KeyboardButton(text=messages_text.BUTTON_EXERCISES_LIST),
               types.KeyboardButton(text=messages_text.BUTTON_SHOW_RESULTS_TABLE))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_ADD),
               types.KeyboardButton(text=messages_text.BUTTON_DELETE))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_SHOW_STATUS))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_EXIT))
    return markup


def get_adding_interface_keyboard(is_super_admin: bool) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_ADD_STUDENT))
    if is_super_admin:
        markup.add(types.KeyboardButton(text=messages_text.BUTTON_ADD_ADMIN))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_ADD_EXERCISE))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_BACK))
    return markup


def get_adding_exercise_interface_keyboard(task_id: int,
                                           number_tasks: int,
                                           is_added_answer: bool,
                                           is_added_task_statement: bool,
                                           is_finished: bool) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if is_added_answer:
        up_row = []
        if task_id > 1:
            up_row.append(types.KeyboardButton(text=messages_text.BUTTON_PREVIOUS_TASK_IN_ADDING_TASK_INTERFACE))
        if task_id < number_tasks:
            up_row.append(types.KeyboardButton(text=messages_text.BUTTON_NEXT_TASK_IN_ADDING_TASK_INTERFACE))
        if len(up_row) == 1:
            markup.add(up_row[0])
        elif len(up_row) == 2:
            markup.add(up_row[0], up_row[1])

    markup.add(types.KeyboardButton(text=messages_text.BUTTON_ADD_ANSWER_ON_TASK))
    if not is_added_task_statement:
        markup.add(types.KeyboardButton(text=messages_text.BUTTON_ADD_STATEMENT_FOR_TASK))

    if not is_finished:
        markup.add(types.KeyboardButton(text=messages_text.BUTTON_BACK))
    else:
        markup.add(types.KeyboardButton(text=messages_text.BUTTON_FINISH_CREATING_EXERCISE))
    return markup


def get_deleting_interface_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_DELETE_ACCOUNT))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_DELETE_EXERCISE))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_BACK))
    return markup
