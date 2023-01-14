import threading
import telebot
from telebot import types
import config
import constants


class WaitModeDescription:
    def __init__(self, function, status=None, data=None):
        self.function = function
        self.status = status
        self.data = data


class TelegramClient:
    def __init__(self):
        self.client = None
        self.handler_thread = None
        self.wait_mode = dict()

    def __is_super_admin(self, id):
        return False

    def __is_admin(self, id):
        return False

    def __is_valid_login(self, login):
        return False

    def __is_valid_password(self, login, password):
        return False

    def __is_authorized(self, id):
        return False

    def __sign_out(self, login):
        return 0  # delogined id (None if not)

    def __sign_up(self, login, id):
        pass

    def __get_markup(self, id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if self.wait_mode[id] is not None:
            return markup

        if not self.__is_authorized(id):
            markup.add(types.KeyboardButton(text="Авторизоваться"))

        return markup

    def __send_message(self, id, text, markup=None):
        if markup is None:
            self.client.send_message(id, text=text)
        else:
            self.client.send_message(id, text=text, reply_markup=markup)

    def __compute_command_start(self, message):
        if not self.__is_authorized(message.chat.id):
            text = "Пожалуйста, авторизуйтесь."

        self.__send_message(message.chat.id, text, markup=self.__get_markup(message))

    def __compute_keyboard_sign_up(self, message):
        if self.__is_authorized(message.chat.id):
            self.__send_message(message.chat.id, "Вы уже были авторизованны.", markup=self.__get_markup(message))
            return

        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_sign_up, status="WAIT_LOGIN")
            self.client.send_message(message.chat.id, text="Введите лигон аккаунта для авторизации:", markup=self.__get_markup(message))
            return

        if self.wait_mode[message.chat.id].status == "WAIT_LOGIN":
            if not self.__is_valid_login(message.text):
                self.wait_mode[message.chat.id] = None
                self.client.send_message(message.chat.id, text="Введённый логин не существует, авторизация отменена.", markup=self.__get_markup(message))
                return

            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_sign_up, status="WAIT_PASSWORD", data=message.text)
            self.client.send_message(message.chat.id, text="Введите пароль:", markup=self.__get_markup(message))
            return

        if self.wait_mode[message.chat.id].status == "WAIT_PASSWORD":
            login = self.wait_mode[message.chat.id].data
            password = message.text

            self.wait_mode[message.chat.id] = None
            if not self.__is_valid_password(login, password):
                self.client.send_message(message.chat.id, text="Введённый неправильный пароль, авторизация отменена.", markup=self.__get_markup(message))
                return

            last_id = self.__sign_out(login)
            if last_id is not None:
                self.client.send_message(last_id, text="В ваш профиль выполнен вход с другого телеграм аккаунта, вы были разлогинены.")

            self.__sign_up(login, message.chat.id)
            self.client.send_message(message.chat.id, text="Успешная авторизация!", reply_markup=self.__get_markup(message))
            return

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

            if self.wait_mode[message.chat.id] is not None:
                self.wait_mode[message.chat.id]["function"](message)
            elif message.text == "Авторизоваться":
                self.__compute_keyboard_sign_up(message)

        self.client.infinity_polling()

    def run(self):
        self.client = telebot.TeleBot(config.TELEGRAM_TOKEN)
        self.handler_thread = threading.Thread(target=self.__handler)
        self.handler_thread.start()
