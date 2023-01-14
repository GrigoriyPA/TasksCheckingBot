import threading
from telebot import types, TeleBot
from user import User
from database.database_funcs import DatabaseHelper
import config
import constants


def add_error_to_log(text):
    error_log = open(constants.PATH_TO_ERROR_LOG + constants.ERROR_LOG_NAME, "a")
    error_log.write(text + "\n\n")
    error_log.close()


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

        self.data_base = DatabaseHelper(constants.PATH_TO_DATABASE, constants.DATABASE_NAME)
        # self.data_base.create_database()

    def __is_super_admin(self, id):
        user = self.data_base.get_user_by_telegram_id(id)
        return user is not None and user.status == constants.SUPER_ADMIN

    def __is_admin(self, id):
        user = self.data_base.get_user_by_telegram_id(id)
        return user is not None and (user.status == constants.ADMIN or user.status == constants.SUPER_ADMIN)

    def __is_valid_login(self, login):
        return self.data_base.get_user_by_login(login) is not None

    def __is_valid_password(self, login, password):
        user = self.data_base.get_user_by_login(login)
        if user is None:
            add_error_to_log("Invalid login in function __is_valid_password")
            return None

        return user.password == password

    def __is_authorized(self, id):
        return self.data_base.get_user_by_telegram_id(id) is not None

    def __get_login_by_id(self, id):
        user = self.data_base.get_user_by_telegram_id(id)

        if user is None:
            return None
        return user.login

    def __get_id_by_login(self, login):
        user = self.data_base.get_user_by_login(login)

        if user is None or user.telegram_id == constants.UNAUTHORIZED_TELEGREM_ID:
            return None
        return user.telegram_id

    def __get_markup(self, id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if id in self.wait_mode and self.wait_mode[id] is not None:
            return types.ReplyKeyboardRemove()

        if not self.__is_authorized(id):
            markup.add(types.KeyboardButton(text="Авторизоваться"))
            return markup

        if self.__is_admin(id):
            markup.add(types.KeyboardButton(text="Добавить аккаунт"), types.KeyboardButton(text="Удалить аккаунт"))
        if self.__is_super_admin(id):
            markup.add(types.KeyboardButton(text="Добавить адм."), types.KeyboardButton(text="Удалить адм."))

        markup.add(types.KeyboardButton(text="Выйти"))
        return markup

    def __add_user(self, id):
        if id not in self.wait_mode:
            self.wait_mode[id] = None

    def __sign_out(self, id):
        user = self.data_base.get_user_by_telegram_id(id)
        if user is None:
            add_error_to_log("Invalid id in function __sign_out")
            return None

        self.data_base.change_user_telegram_id(user.login, constants.UNAUTHORIZED_TELEGREM_ID)

    def __sign_up(self, login, id):
        user = self.data_base.get_user_by_login(login)
        if user is None:
            add_error_to_log("Invalid login in function __sign_out")
            return None

        self.data_base.change_user_telegram_id(user.login, id)

    def __add_admin(self, login):
        user = self.data_base.get_user_by_login(login)
        if user is None:
            add_error_to_log("Invalid login in function __add_admin")
            return None

        self.data_base.change_user_status(user.login, constants.ADMIN)

    def __delete_admin(self, login):
        user = self.data_base.get_user_by_login(login)
        if user is None:
            add_error_to_log("Invalid login in function __delete_admin")
            return None

        self.data_base.change_user_status(user.login, constants.USER)

    def __send_message(self, id, text, markup=None):
        if markup is None:
            self.client.send_message(id, text=text)
        else:
            self.client.send_message(id, text=text, reply_markup=markup)

    def __compute_command_start(self, message):
        text = "С возвращением!"
        if not self.__is_authorized(message.chat.id):
            text = "Пожалуйста, авторизуйтесь."

        self.__send_message(message.chat.id, text, markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_sign_up(self, message):
        if self.__is_authorized(message.chat.id):
            self.wait_mode[message.chat.id] = None
            self.__send_message(message.chat.id, "Вы уже были авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_sign_up, status="WAIT_LOGIN")
            self.__send_message(message.chat.id, "Введите логин аккаунта для авторизации:",
                                markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id].status == "WAIT_LOGIN":
            login = message.text
            if not self.__is_valid_login(login):
                self.wait_mode[message.chat.id] = None
                self.__send_message(message.chat.id, "Введённый логин не существует, авторизация отменена.",
                                    markup=self.__get_markup(message.chat.id))
                return

            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_sign_up, data=login)
            self.__send_message(message.chat.id, "Введите пароль:", markup=self.__get_markup(message.chat.id))
            return

        login = self.wait_mode[message.chat.id].data
        password = message.text
        self.wait_mode[message.chat.id] = None
        if not self.__is_valid_password(login, password):
            self.__send_message(message.chat.id, "Введённый неправильный пароль, авторизация отменена.",
                                markup=self.__get_markup(message.chat.id))
            return

        id = self.__get_id_by_login(login)
        self.__sign_up(login, message.chat.id)
        if id is not None:
            self.__send_message(id, "В ваш профиль выполнен вход с другого телеграм аккаунта, вы были разлогинены.", markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Успешная авторизация!", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_sign_out(self, message):
        if not self.__is_authorized(message.chat.id):
            self.__send_message(message.chat.id, "Вы не авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        self.__sign_out(message.chat.id)
        self.__send_message(message.chat.id, "Вы вышли из аккаунта.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add_account(self, message):
        if not self.__is_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_account, status="WAIT_LOGIN")
            self.__send_message(message.chat.id, "Введите логин для нового аккаунта:", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id].status == "WAIT_LOGIN":
            login = message.text
            if self.__is_valid_login(message.text):
                self.wait_mode[message.chat.id] = None
                self.__send_message(message.chat.id, "Введённый логин уже существует, создание аккаунта отменено.", markup=self.__get_markup(message.chat.id))
                return

            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_account, data=login)
            self.__send_message(message.chat.id, "Введите пароль для нового аккаунта:", markup=self.__get_markup(message.chat.id))
            return

        login = self.wait_mode[message.chat.id].data
        password = message.text
        self.wait_mode[message.chat.id] = None

        self.data_base.create_user(User(login, password, constants.USER, constants.UNAUTHORIZED_TELEGREM_ID))
        self.__send_message(message.chat.id, "Аккаунт успешно создан.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete_account(self, message):
        if not self.__is_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete_account)
            self.__send_message(message.chat.id, "Введите логин аккаунта для удаления:", markup=self.__get_markup(message.chat.id))
            return

        login = message.text
        status = self.data_base.get_user_by_login(login).status
        self.wait_mode[message.chat.id] = None
        if status == constants.SUPER_ADMIN or not self.__is_super_admin(message.chat.id) and status == constants.ADMIN:
            self.__send_message(message.chat.id, "Введите не можете удалить этот аккаунт.", markup=self.__get_markup(message.chat.id))
            return

        if not self.__is_valid_login(message.text):
            self.__send_message(message.chat.id, "Введённый логин не существует, удаление аккаунта отменено.", markup=self.__get_markup(message.chat.id))
            return

        # delete user
        self.__send_message(message.chat.id, "Аккаунт успешно удалён.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add_admin(self, message):
        if not self.__is_super_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_admin)
            self.__send_message(message.chat.id, "Введите логин аккаунта для выдачи прав администратора:", markup=self.__get_markup(message.chat.id))
            return

        login = message.text
        self.wait_mode[message.chat.id] = None
        if not self.__is_valid_login(message.text):
            self.__send_message(message.chat.id, "Введённый логин не существует, модификация прав отменена.", markup=self.__get_markup(message.chat.id))
            return

        self.__add_admin(login)
        id = self.__get_id_by_login(login)
        if id is not None:
            self.__send_message(id, "Вам выданы права администратора.", markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Команда успешно выполненна.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete_admin(self, message):
        if not self.__is_super_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete_admin)
            self.__send_message(message.chat.id, "Введите логин аккаунта для лишения прав администратора:", markup=self.__get_markup(message.chat.id))
            return

        login = message.text
        self.wait_mode[message.chat.id] = None
        if not self.__is_valid_login(message.text):
            self.__send_message(message.chat.id, "Введённый логин не существует, модификация прав отменена.", markup=self.__get_markup(message.chat.id))
            return

        if self.data_base.get_user_by_login(login).status == constants.SUPER_ADMIN:
            self.__send_message(message.chat.id, "Запрещено менять права доступа этого пользователя.", markup=self.__get_markup(message.chat.id))
            return

        self.__delete_admin(login)
        id = self.__get_id_by_login(login)
        if id is not None:
            self.__send_message(id, "Вы лишены прав администратора.", markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Команда успешно выполненна.", markup=self.__get_markup(message.chat.id))

    def __handler(self):
        print("TG client started.")

        @self.client.message_handler(commands=['start'])
        def start(message):
            self.__add_user(message.chat.id)
            self.__compute_command_start(message)

        @self.client.message_handler(content_types=["text"])
        def on_message(message):
            # If message from chat -> skip
            if message.chat.id != message.from_user.id:
                return
            self.__add_user(message.chat.id)

            if self.wait_mode[message.chat.id] is not None:
                self.wait_mode[message.chat.id].function(message)
            elif message.text == "Авторизоваться":
                self.__compute_keyboard_sign_up(message)
            elif message.text == "Выйти":
                self.__compute_keyboard_sign_out(message)
            elif message.text == "Добавить аккаунт":
                self.__compute_keyboard_add_account(message)
            elif message.text == "Удалить аккаунт":
                self.__compute_keyboard_delete_account(message)
            elif message.text == "Добавить адм.":
                self.__compute_keyboard_add_admin(message)
            elif message.text == "Удалить адм.":
                self.__compute_keyboard_delete_admin(message)
            else:
                self.__send_message(message.chat.id, "Неизвестная команда.")

        self.client.infinity_polling()

    def run(self):
        self.client = TeleBot(config.TELEGRAM_TOKEN)
        self.handler_thread = threading.Thread(target=self.__handler)
        self.handler_thread.start()
