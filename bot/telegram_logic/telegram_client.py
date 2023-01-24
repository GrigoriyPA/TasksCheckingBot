from collections.abc import Callable
from bot.telegram_logic.inner_types import MARKUP_TYPES, Callback, Message, Attachment
from telebot import TeleBot, types
from threading import Thread
from typing import Optional


class TelegramClient:
    def __init__(self, action_on_message: Optional[Callable[[Message], None]] = None,
                 action_on_callback: Optional[Callable[[Callback], None]] = None) -> None:
        self.__token: Optional[str] = None  # Token of current session
        self.__client: Optional[TeleBot] = None  # Telebot client object
        self.__handler_thread: Optional[Thread] = None  # Thread of message handler

        self.action_on_message = action_on_message  # Function that called on client message
        self.action_on_callback = action_on_callback  # Function that called on callback from inline button

    def __get_attachment(self, message: types.Message) -> Optional[Attachment]:
        # Getting message attachment

        if message.content_type == "text":
            # There is no attachment
            return None

        file = None

        if message.content_type == "photo":
            # Attachment is compressed photo
            file = self.__client.get_file(message.photo[-1].file_id)

        if message.content_type == "document":
            # Attachment is some document
            file = self.__client.get_file(message.document.file_id)

        # Unknown attachment type
        if file is None:
            return None

        link = "https://api.telegram.org/file/bot" + self.__token + "/" + file.file_path

        return Attachment(attach_type=message.content_type, link=link)

    def __handler(self) -> None:
        # This function is called on all events

        print("TG client started.")

        @self.__client.callback_query_handler(func=lambda call: True)
        def callback_inline(call: types.CallbackQuery) -> None:
            # Computing callback from inline button

            # Answer on callback (required to continue working with the button)
            self.__client.answer_callback_query(callback_query_id=call.id)

            # If there is no action on callback defined, exit from function
            if self.action_on_callback is None:
                return

            from_id: int = call.message.chat.id
            author: types.ChatMember = self.__client.get_chat_member(from_id, call.from_user.id)
            message_id: int = call.message.message_id
            text: str = call.message.text

            self.action_on_callback(Callback(from_id=from_id, callback_data=call.data, message_id=message_id, text=text,
                                             author=author))

        @self.__client.message_handler(content_types=["text", "photo", "document"])
        def on_message(message: types.Message) -> None:
            # Computing user massage

            # If there is no action on message defined, exit from function
            if self.action_on_message is None:
                return

            from_id: int = message.chat.id
            author: types.ChatMember = self.__client.get_chat_member(from_id, message.from_user.id)

            text: str = ""
            if message.content_type == "text":
                text: str = message.text
            elif message.caption is not None:
                text: str = message.caption

            attachment: Optional[Attachment] = self.__get_attachment(message)

            if from_id != message.from_user.id:
                # Current message from chat
                self.action_on_message(Message(from_id=from_id, text=text, attachment=attachment, author=author,
                                               chat_name=message.chat.title))
            else:
                # Current message from user
                self.action_on_message(Message(from_id=from_id, text=text, attachment=attachment, author=author))

        self.__client.infinity_polling()  # Launch bot

    def edit_message(self, from_id: int, message_id: int, text: str, markup: MARKUP_TYPES = None) -> None:
        self.__client.edit_message_text(chat_id=from_id, message_id=message_id, text=text, reply_markup=markup)

    def send_message(self, send_id: int, text: str, attachments: Optional[list[Attachment]] = None,
                     markup: MARKUP_TYPES = None) -> None:
        # If there is no attachments, just send text
        if attachments is None:
            self.__client.send_message(chat_id=send_id, text=text, reply_markup=markup)
            return None

        # Send messages for each attachment
        for attachment in attachments:
            if attachment.attach_type == "photo":
                # Attachment is compressed photo
                self.__client.send_photo(chat_id=send_id, caption=text, photo=attachment.get_content())
            elif attachment.attach_type == "document":
                # Attachment is some document
                self.__client.send_document(chat_id=send_id, caption=text, document=attachment.get_content())

            text = ''  # Drop message text after first message

    def get_chat_member(self, chat_id: int, user_id: int) -> types.ChatMember:
        return self.__client.get_chat_member(chat_id=chat_id, user_id=user_id)

    def run(self, token: str) -> None:
        # Function that launch new session

        # If session already started, stop current session
        if self.__handler_thread is not None:
            self.stop()

        self.__token = token
        self.__client = TeleBot(token)
        self.__handler_thread = Thread(target=self.__handler)
        self.__handler_thread.start()

    def stop(self) -> None:
        # Function stops current session

        if self.__handler_thread is not None:
            self.__client.stop_polling()
            self.__handler_thread.join()
            self.__handler_thread: Optional[Thread] = None
