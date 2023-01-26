import requests
from telebot import types
from typing import Optional, Union

MARKUP_TYPES = Optional[
    Union[types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup, types.ReplyKeyboardRemove, types.ForceReply]]


class Attachment:
    def __init__(self, attach_type: str = "document", link: Optional[str] = None, data: Optional[bytes] = None,
                 file_name: Optional[str] = None) -> None:
        self.attach_type = attach_type
        self.data = data
        self.link = link
        self.file_name = file_name

        if self.data is None:
            self.data = requests.get(self.link).content

    def get_content(self) -> bytes:
        # Returns data of current link

        return self.data

    def get_extension(self) -> str:
        # Returns extension of data on current link

        if self.link is None:
            return ""

        return self.link[self.link.rfind(".") + 1:len(self.link)]


class Message:
    def __init__(self, from_id: int, text: str, author: types.ChatMember, attachment: Optional[Attachment] = None,
                 chat_name: Optional[str] = None) -> None:
        self.from_id = from_id
        self.text = text
        self.author = author
        self.attachment = attachment
        self.chat_name = chat_name

    def is_from_chat(self) -> bool:
        return self.from_id != self.author.user.id


class Callback:
    def __init__(self, from_id: int, callback_data: str, message_id: int, text: str, author: types.ChatMember) -> None:
        self.from_id = from_id
        self.callback_data = callback_data
        self.message_id = message_id
        self.text = text
        self.author = author

    def is_from_chat(self) -> bool:
        return self.from_id != self.author.user.id
