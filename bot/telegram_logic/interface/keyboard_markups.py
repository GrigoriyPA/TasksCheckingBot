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


def get_deleting_interface_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_DELETE_ACCOUNT))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_DELETE_EXERCISE))
    markup.add(types.KeyboardButton(text=messages_text.BUTTON_BACK))
    return markup
