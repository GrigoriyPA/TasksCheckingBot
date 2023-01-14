import threading
import telebot
import config


class TelegramClient:
    def __init__(self):
        self.client = None
        self.handler_thread = None

    def __compute_command_start(self, message):
        self.client.send_message(message.chat.id, text="Hello!")

    def __handler(self):
        print("TG client started.")

        @self.client.message_handler(commands=['start'])
        def start(message):
            self.__compute_command_start(message)

        @self.client.message_handler(content_types=["text"])
        def on_message(message):
            # If message from chet - skip
            if message.chat.id != message.from_user.id:
                return

        self.client.infinity_polling()

    def run(self):
        self.client = telebot.TeleBot(config.TELEGRAM_TOKEN)
        self.handler_thread = threading.Thread(target=self.__handler)
        self.handler_thread.start()
