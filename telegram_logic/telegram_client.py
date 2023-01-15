import threading
from telebot import types, TeleBot
from user import User
from homework import Homework
from database.database_funcs import DatabaseHelper
import markups
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

    def __check_homework(self, homework_name):
        pass

    def __check_task(self, homework_name, task_id):
        pass

    def __is_super_admin(self, id):
        user = self.data_base.get_user_by_telegram_id(id)
        return user is not None and user.status == constants.SUPER_ADMIN

    def __is_admin(self, id):
        user = self.data_base.get_user_by_telegram_id(id)
        return user is not None and (user.status == constants.ADMIN or user.status == constants.SUPER_ADMIN)

    def __get_login_by_id(self, id):
        user = self.data_base.get_user_by_telegram_id(id)

        if user is None:
            return None
        return user.login

    def __get_id_by_login(self, login):
        user = self.data_base.get_user_by_login(login)
        if user is None:
            add_error_to_log("Invalid login in function __get_id_by_login")
            return None

        if user.telegram_id == constants.UNAUTHORIZED_TELEGREM_ID:
            return None
        return user.telegram_id

    def __get_markup(self, id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if id in self.wait_mode and self.wait_mode[id] is not None:
            if self.wait_mode[id].status == "ADMIN_ACTION" or self.wait_mode[id].status == "SUPER_ADMIN_ACTION":
                markup.add(types.KeyboardButton(text="Аккаунт"))
                markup.add(types.KeyboardButton(text="Задание"))

            if self.wait_mode[id].status == "SUPER_ADMIN_ACTION":
                markup.add(types.KeyboardButton(text="Администратор"))

            markup.add(types.KeyboardButton(text="Назад"))
            return markup

        if self.data_base.get_user_by_telegram_id(id) is None:
            markup.add(types.KeyboardButton(text="Авторизоваться"))
            return markup

        if self.__is_admin(id):
            markup.add(types.KeyboardButton(text="Добавить"), types.KeyboardButton(text="Удалить"))
        else:
            markup.add(types.KeyboardButton(text="Сдать задачу"))

        markup.add(types.KeyboardButton(text="Выйти"))
        return markup

    def __send_message(self, id, text, markup=None):
        if markup is None:
            self.client.send_message(id, text=text)
        else:
            self.client.send_message(id, text=text, reply_markup=markup)

    def __compute_command_start(self, message):
        text = "С возвращением!"
        if self.data_base.get_user_by_telegram_id(message.chat.id) is None:
            text = "Пожалуйста, авторизуйтесь."

        self.__send_message(message.chat.id, text, markup=self.__get_markup(message.chat.id))

    def __compute_wait_answer(self, message):
        self.wait_mode[message.chat.id] = None
        answer = message.text
        self.__send_message(message.chat.id, "К сожалению, ответы мы проверять не умеем)", markup=self.__get_markup(message.chat.id))

    def __compute_callback_select_homework(self, data, message):
        homework_name = data[0]
        if not self.__check_homework(homework_name):
            self.__send_message(message.chat.id, "Выбранная работа недоступна.", markup=self.__get_markup(message.chat.id))
            return

        markup = markups.get_task_list("????", "?????", self.__check_task)
        self.__send_message(message.chat.id, "Выберите задание.", markup=markup)

    def __compute_callback_select_task(self, data, message):
        homework_name, task_id = data[0], int(data[1])
        if not self.__check_task(homework_name, task_id):
            self.__send_message(message.chat.id, "Выбранное задание недоступно.", markup=self.__get_markup(message.chat.id))
            return

        self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_wait_answer)
        self.__send_message(message.chat.id, "Введите ответ на задание " + str(task_id) + ":", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_back(self, message):
        self.wait_mode[message.chat.id] = None
        self.__send_message(message.chat.id, "Выход выполнен.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_sign_up(self, message):
        if self.data_base.get_user_by_telegram_id(message.chat.id) is not None:
            self.wait_mode[message.chat.id] = None
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_sign_up, status="WAIT_LOGIN")
            self.__send_message(message.chat.id, "Введите логин аккаунта для авторизации:",
                                markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id].status == "WAIT_LOGIN":
            login = message.text
            if self.data_base.get_user_by_login(login) is None:
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
        if self.data_base.get_user_by_login(login).password != password:
            self.__send_message(message.chat.id, "Введённый неправильный пароль, авторизация отменена.",
                                markup=self.__get_markup(message.chat.id))
            return

        id = self.__get_id_by_login(login)
        self.data_base.change_user_telegram_id(login, message.chat.id)
        if id is not None:
            self.__send_message(id, "В ваш профиль выполнен вход с другого телеграм аккаунта, вы были разлогинены.", markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Успешная авторизация!", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_sign_out(self, message):
        user = self.data_base.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        self.data_base.change_user_telegram_id(user.login, constants.UNAUTHORIZED_TELEGREM_ID)
        self.__send_message(message.chat.id, "Вы вышли из аккаунта.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add_account(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_account, status="WAIT_LOGIN")
            self.__send_message(message.chat.id, "Введите логин для нового аккаунта:", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id].status == "WAIT_LOGIN":
            login = message.text
            if self.data_base.get_user_by_login(login) is not None:
                self.wait_mode[message.chat.id] = None
                self.__send_message(message.chat.id, "Введённый логин уже существует, создание аккаунта отменено.", markup=self.__get_markup(message.chat.id))
                return

            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_account, data=login)
            self.__send_message(message.chat.id, "Введите пароль для нового аккаунта:", markup=self.__get_markup(message.chat.id))
            return

        login = self.wait_mode[message.chat.id].data
        password = message.text
        self.wait_mode[message.chat.id] = None

        self.data_base.add_user(User(login, password, constants.USER, constants.UNAUTHORIZED_TELEGREM_ID))
        self.__send_message(message.chat.id, "Аккаунт успешно создан.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete_account(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete_account)
            self.__send_message(message.chat.id, "Введите логин аккаунта для удаления:", markup=self.__get_markup(message.chat.id))
            return

        login = message.text
        self.wait_mode[message.chat.id] = None
        if self.data_base.get_user_by_login(login) is None:
            self.__send_message(message.chat.id, "Введённый логин не существует, удаление аккаунта отменено.", markup=self.__get_markup(message.chat.id))
            return

        status = self.data_base.get_user_by_login(login).status
        if status == constants.SUPER_ADMIN or not self.__is_super_admin(message.chat.id) and status == constants.ADMIN:
            self.__send_message(message.chat.id, "Вы не можете удалить этот аккаунт.", markup=self.__get_markup(message.chat.id))
            return

        self.data_base.delete_user_by_login(login)
        self.__send_message(message.chat.id, "Аккаунт успешно удалён.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add_admin(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_admin)
            self.__send_message(message.chat.id, "Введите логин аккаунта для выдачи прав администратора:", markup=self.__get_markup(message.chat.id))
            return

        login = message.text
        self.wait_mode[message.chat.id] = None
        if self.data_base.get_user_by_login(login) is None:
            self.__send_message(message.chat.id, "Введённый логин не существует, модификация прав отменена.", markup=self.__get_markup(message.chat.id))
            return

        self.data_base.change_user_status(login, constants.ADMIN)
        id = self.__get_id_by_login(login)
        if id is not None:
            self.__send_message(id, "Вам выданы права администратора.", markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Команда успешно выполненна.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete_admin(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete_admin)
            self.__send_message(message.chat.id, "Введите логин аккаунта для лишения прав администратора:", markup=self.__get_markup(message.chat.id))
            return

        login = message.text
        self.wait_mode[message.chat.id] = None
        if self.data_base.get_user_by_login(login) is None:
            self.__send_message(message.chat.id, "Введённый логин не существует, модификация прав отменена.", markup=self.__get_markup(message.chat.id))
            return

        if self.data_base.get_user_by_login(login).status == constants.SUPER_ADMIN:
            self.__send_message(message.chat.id, "Запрещено менять права доступа этого пользователя.", markup=self.__get_markup(message.chat.id))
            return

        self.data_base.change_user_status(login, constants.USER)
        id = self.__get_id_by_login(login)
        if id is not None:
            self.__send_message(id, "Вы лишены прав администратора.", markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Команда успешно выполненна.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add_exercise(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_exercise, status="WAIT_NAME")
            self.__send_message(message.chat.id, "Введите имя нового задания:", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id].status == "WAIT_NAME":
            homework_name = message.text
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_exercise, data={"name": homework_name, "answers": []}, status="WAIT_NUMBER_OF_EXERCISES")
            self.__send_message(message.chat.id, "Введите количество заданий:", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id].status == "WAIT_NUMBER_OF_EXERCISES":
            success = True
            number = 0
            try:
                number = int(message.text)
            except:
                success = False
            if not success or number <= 0:
                self.wait_mode[message.chat.id] = None
                self.__send_message(message.chat.id, "Введено некорректное число задач, создание задания отменено.", markup=self.__get_markup(message.chat.id))
                return

            self.wait_mode[message.chat.id].status = {"current_number": 0, "amount": number}

        if self.wait_mode[message.chat.id].status["current_number"] > 0:
            self.wait_mode[message.chat.id].data["answers"].append(message.text)
            self.__send_message(message.chat.id, "Ответ принят.", markup=self.__get_markup(message.chat.id))

        if self.wait_mode[message.chat.id].status["current_number"] < self.wait_mode[message.chat.id].status["amount"]:
            self.wait_mode[message.chat.id].status["current_number"] += 1
            self.__send_message(message.chat.id, "Введите ответ к задаче номер " + str(self.wait_mode[message.chat.id].status["current_number"]) + ":", markup=self.__get_markup(message.chat.id))
            return

        homework_name = self.wait_mode[message.chat.id].data["name"]
        answers = self.wait_mode[message.chat.id].data["answers"]
        self.wait_mode[message.chat.id] = None

        self.data_base.add_homework(Homework(homework_name, answers))
        self.__send_message(message.chat.id, "Задание успешно добавленно.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete_exercise(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete_exercise)
            self.__send_message(message.chat.id, "Введите имя задания для удаления.", markup=self.__get_markup(message.chat.id))
            return

        homework_name = message.text
        self.wait_mode[message.chat.id] = None

        self.data_base.delete_homework_by_name(homework_name)
        self.__send_message(message.chat.id, "Задание успешно удалено.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add(self, message):
        if self.wait_mode[message.chat.id] is None:
            if self.__is_super_admin(message.chat.id):
                self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add, status="SUPER_ADMIN_ACTION", data="ADD")
            else:
                self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add, status="ADMIN_ACTION", data="ADD")

            self.__send_message(message.chat.id, "Выберите объект модификации.", markup=self.__get_markup(message.chat.id))
            return

        self.wait_mode[message.chat.id] = None
        if message.text == "Аккаунт" and self.__is_admin(message.chat.id):
            self.__compute_keyboard_add_account(message)
        elif message.text == "Задание" and self.__is_admin(message.chat.id):
            self.__compute_keyboard_add_exercise(message)
        elif message.text == "Администратор" and self.__is_super_admin(message.chat.id):
            self.__compute_keyboard_add_admin(message)
        else:
            self.__send_message(message.chat.id, "Неизвестная команда, отмена модификации.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete(self, message):
        if self.wait_mode[message.chat.id] is None:
            if self.__is_super_admin(message.chat.id):
                self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete, status="SUPER_ADMIN_ACTION", data="DELETE")
            else:
                self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete, status="ADMIN_ACTION", data="DELETE")

            self.__send_message(message.chat.id, "Выберите объект модификации.", markup=self.__get_markup(message.chat.id))
            return

        self.wait_mode[message.chat.id] = None
        if message.text == "Аккаунт" and self.__is_admin(message.chat.id):
            self.__compute_keyboard_delete_account(message)
        elif message.text == "Задание" and self.__is_admin(message.chat.id):
            self.__compute_keyboard_delete_exercise(message)
        elif message.text == "Администратор" and self.__is_super_admin(message.chat.id):
            self.__compute_keyboard_delete_admin(message)
        else:
            self.__send_message(message.chat.id, "Неизвестная команда, отмена модификации.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_send_answer(self, message):
        user = self.data_base.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        markup = markups.get_homework_list("????", self.__check_homework)
        self.__send_message(message.chat.id, "Выберите имя работы.", markup=markup)

    def __handler(self):
        print("TG client started.")

        @self.client.message_handler(commands=['start'])
        def start(message):
            self.__compute_command_start(message)

        @self.client.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            self.client.answer_callback_query(callback_query_id=call.id)
            data = call.data.split()
            if data[0] == "SELECT_HOMEWORK":
                self.__compute_callback_select_homework(data[1:], call.message)
            elif data[0] == "SELECT_TASK":
                self.__compute_callback_select_task(data[1:], call.message)
            else:
                add_error_to_log("Unknown callback: " + data[0])

        @self.client.message_handler(content_types=["text"])
        def on_message(message):
            if message.chat.id != message.from_user.id:
                return

            if message.chat.id not in self.wait_mode:
                self.wait_mode[message.chat.id] = None

            if self.wait_mode[message.chat.id] is not None:
                if message.text == "Назад":
                    self.__compute_keyboard_back(message)
                else:
                    self.wait_mode[message.chat.id].function(message)
            elif message.text == "Авторизоваться":
                self.__compute_keyboard_sign_up(message)
            elif message.text == "Выйти":
                self.__compute_keyboard_sign_out(message)
            elif message.text == "Сдать задачу" and not self.__is_admin(message.chat.id):
                self.__compute_keyboard_send_answer(message)
            elif message.text == "Добавить" and self.__is_admin(message.chat.id):
                self.__compute_keyboard_add(message)
            elif message.text == "Удалить" and self.__is_admin(message.chat.id):
                self.__compute_keyboard_delete(message)
            else:
                self.__send_message(message.chat.id, "Неизвестная команда.")

        self.client.infinity_polling()

    def run(self):
        self.client = TeleBot(config.TELEGRAM_TOKEN)
        self.handler_thread = threading.Thread(target=self.__handler)
        self.handler_thread.start()
