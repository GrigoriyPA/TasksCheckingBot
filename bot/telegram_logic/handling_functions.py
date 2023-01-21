from bot.telegram_logic import keyboard_markups
from bot.telegram_logic.user_handler import UserHandler
from typing import Any, Callable


def default_state(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    if handler.is_admin(from_id):
        handler.send_message(send_id=from_id, text="С возвращением, администратор.",
                             markup=keyboard_markups.get_default_admin_keyboard())
        return default_admin_page, None

    if handler.is_student(from_id):
        handler.send_message(send_id=from_id, text="С возвращением, ученик.",
                             markup=keyboard_markups.get_default_admin_keyboard())
        return default_student_page, None


def unauthorized_user(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    handler.send_message(from_id, "BOB!")
    return default_state, None


def default_student_page(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    handler.send_message(from_id, "BOB!")
    return default_state, None


def default_admin_page(handler: UserHandler, from_id: int, text: str, data) -> tuple[Callable, Any]:
    handler.send_message(from_id, "BOB!")
    return default_state, None
