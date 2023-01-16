from telebot import types, TeleBot
from user import User
from homework import Homework
from database.database_funcs import DatabaseHelper
from telegram_logic import markups
import config
import constants


def add_error_to_log(text):
    error_log = open(constants.PATH_TO_ERROR_LOG + constants.ERROR_LOG_NAME, "a")
    error_log.write(text + "\n\n")
    error_log.close()


class WaitModeDescription:
    # A class that stores a description of the user input waiting mode (for example, when entering a login and password)

    def __init__(self, function, status=None, data=None):
        self.function = function  # function that will call on next user input
        self.status = status  # Current status of structure
        self.data = data  # Current data of structure


class TelegramClient:
    def __init__(self):
        self.client = None  # Telebot client object
        self.wait_mode = dict()  # Dict of { telegram_id -> WaitModeDescription }

        self.database = DatabaseHelper(constants.PATH_TO_DATABASE, constants.DATABASE_NAME)  # Main database
        # self.database.create_database()

    def __check_name(self, name: str):
        # Check login/homework name, returns True if all ASCII codes are good
        for symbol in name:
            if ord(symbol) >= 123:
                return False
        return True

    def __check_task(self, login: str, homework_name: str, task_id: int):
        user = self.database.get_user_by_login(login)

        # If there is no such user just return None
        if user is None:
            return False

        user_answer = self.database.get_user_answer_for_the_task(login, homework_name, task_id)

        # If user did not give any answers just return None
        if user_answer is None or user_answer == '':
            return None

        # Returns True if user answer is right
        return self.database.get_right_answer_for_the_task(homework_name, task_id) == user_answer

    def __is_super_admin(self, id):
        user = self.database.get_user_by_telegram_id(id)

        # Returns True if user exists and his status is SUPER_ADMIN
        return user is not None and user.status == constants.SUPER_ADMIN

    def __is_admin(self, id):
        user = self.database.get_user_by_telegram_id(id)

        # Returns True if user exists and his status is ADMIN or SUPER_ADMIN
        return user is not None and (user.status == constants.ADMIN or user.status == constants.SUPER_ADMIN)

    def __get_login_by_id(self, id):
        user = self.database.get_user_by_telegram_id(id)

        # If there is no such user just return None
        if user is None:
            return None

        return user.login

    def __get_id_by_login(self, login):
        user = self.database.get_user_by_login(login)

        # If there is no such user send error to error log
        if user is None:
            add_error_to_log("Invalid login in function __get_id_by_login")
            return None

        # If no one is logged in this account just return None
        if user.telegram_id == constants.UNAUTHORIZED_TELEGRAM_ID:
            return None

        return user.telegram_id

    def __get_markup(self, id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Buttons description on bottom bar

        # Buttons in case when waiting input from user
        if id in self.wait_mode and self.wait_mode[id] is not None:
            if self.wait_mode[id].status == "ADMIN_ACTION" or self.wait_mode[id].status == "SUPER_ADMIN_ACTION":
                # Buttons for admins
                markup.add(types.KeyboardButton(text="Аккаунт"))  # Action with account
                markup.add(types.KeyboardButton(text="Задание"))  # Action with exercise

            if self.wait_mode[id].status == "SUPER_ADMIN_ACTION":
                # Button for super-admins
                markup.add(types.KeyboardButton(text="Администратор"))  # Action with access rights

            # Default waiting-mode button
            markup.add(types.KeyboardButton(text="Назад"))
            return markup

        # Buttons in case when user is not authorized
        if self.database.get_user_by_telegram_id(id) is None:
            markup.add(types.KeyboardButton(text="Авторизоваться"))
            return markup

        # Buttons in the normal situation
        if self.__is_admin(id):
            # Buttons for admins
            markup.add(types.KeyboardButton(text="Добавить"), types.KeyboardButton(text="Удалить"))
            markup.add(types.KeyboardButton(text="Вывести результаты"))
            markup.add(types.KeyboardButton(text="Список аккаунтов"))
            markup.add(types.KeyboardButton(text="Список заданий"))
        else:
            # Buttons for users
            markup.add(types.KeyboardButton(text="Сдать задачу"))
            markup.add(types.KeyboardButton(text="Вывести результаты"))

        # Default button for authorized users
        markup.add(types.KeyboardButton(text="Выйти"))
        return markup

    def __send_message(self, id, text, markup=None):
        if markup is None:
            self.client.send_message(id, text=text)
        else:
            self.client.send_message(id, text=text, reply_markup=markup)

    def __compute_command_start(self, message):
        text = "С возвращением!"
        if self.database.get_user_by_telegram_id(message.chat.id) is None:
            text = "Пожалуйста, авторизуйтесь."

        self.__send_message(message.chat.id, text, markup=self.__get_markup(message.chat.id))

    def __compute_wait_answer(self, message):
        homework_name = self.wait_mode[message.chat.id].data["homework_name"]
        task_id = self.wait_mode[message.chat.id].data["task_id"]
        self.wait_mode[message.chat.id] = None
        if self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Сдача задания невозможна.", markup=self.__get_markup(message.chat.id))
            return

        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        if self.__check_task(user.login, homework_name, task_id) is not None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.", markup=self.__get_markup(message.chat.id))
            return

        answer = message.text
        if answer == '':
            self.__send_message(message.chat.id, "Введён некорректный ответ, сдача задания отменена.", markup=self.__get_markup(message.chat.id))
            return

        correct_answer = self.database.send_answer_for_the_task(user.login, homework_name, task_id, answer)
        if answer == correct_answer:
            result = "✅"
            self.__send_message(message.chat.id, "Ваш ответ правильный!", markup=self.__get_markup(message.chat.id))
        else:
            result = "❌"
            self.__send_message(message.chat.id, "Ваш ответ неправильный. Правильный ответ: " + correct_answer, markup=self.__get_markup(message.chat.id))

        for admin in self.database.get_all_users_with_status(constants.ADMIN) + self.database.get_all_users_with_status(constants.SUPER_ADMIN):
            id = self.__get_id_by_login(admin.login)
            if id is None:
                continue

            self.__send_message(id, user.login + " добавил ответ к заданию " + str(task_id) + " в работе \'" + homework_name + "\'\nПравильный ответ: " + correct_answer + "\nОтвет ученика: " + answer + "\nРезультат: " + result, markup=self.__get_markup(id))

    def __compute_callback_select_homework(self, data, message):
        if self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Выбор задания невозможен.", markup=self.__get_markup(message.chat.id))
            return

        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        homework_name = data[0]
        if self.database.get_homework_by_name(homework_name) is None:
            self.__send_message(message.chat.id, "Выбранная работа недоступна.", markup=self.__get_markup(message.chat.id))
            return

        homework = self.database.get_homework_by_name(homework_name)
        markup = markups.get_task_list(user.login, len(homework.right_answers), homework.name, self.__check_task)
        self.__send_message(message.chat.id, "Выберите задание.", markup=markup)

    def __compute_callback_select_task(self, data, message):
        if self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Выбор задания невозможен.", markup=self.__get_markup(message.chat.id))
            return

        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        homework_name, task_id = data[0], int(data[1])
        homework = self.database.get_homework_by_name(homework_name)
        if self.database.get_homework_by_name(homework_name) is None:
            self.__send_message(message.chat.id, "Выбранная работа недоступна.", markup=self.__get_markup(message.chat.id))
            return

        markup = markups.get_task_list(user.login, len(homework.right_answers), homework.name, self.__check_task)
        try:
            self.client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=message.text, reply_markup=markup)
        except:
            pass

        if self.__check_task(user.login, homework_name, task_id) is not None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.", markup=self.__get_markup(message.chat.id))
            return

        self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_wait_answer, data={"homework_name": homework_name, "task_id": task_id})
        self.__send_message(message.chat.id, "Введите ответ на задание " + str(task_id) + ":", markup=self.__get_markup(message.chat.id))

    def __compute_callback_show_homework(self, data, message):
        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        homework_name = data[0]
        homework = self.database.get_homework_by_name(homework_name)
        if homework is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.", markup=self.__get_markup(message.chat.id))
            return

        markup = markups.get_results_table(self.database.get_results(constants.USER, homework_name), homework_name, len(homework.right_answers), 1)
        self.__send_message(message.chat.id, "Текущие результаты по работе \'" + homework_name + "\':", markup=markup)

    def __compute_callback_show_task(self, data, message):
        if self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Просмотр задания невозможен.", markup=self.__get_markup(message.chat.id))
            return

        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        homework_name, task_id = data[0], int(data[1])
        answer = self.database.get_user_answer_for_the_task(user.login, homework_name, task_id)
        correct_answer = self.database.get_right_answer_for_the_task(homework_name, task_id)
        if answer is None or correct_answer is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.", markup=self.__get_markup(message.chat.id))
            return

        if answer != correct_answer:
            self.__send_message(message.chat.id, "Ваш ответ: " + answer + "\nПравильный ответ: " + correct_answer, markup=self.__get_markup(message.chat.id))
        else:
            self.__send_message(message.chat.id, "Ваш правильный ответ: " + answer, markup=self.__get_markup(message.chat.id))

    def __compute_callback_show_task_in_table(self, data, message):
        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        login, homework_name, task_id = data[0], data[1], int(data[2])
        if not self.__is_admin(message.chat.id) and login != user.login:
            return

        answer = self.database.get_user_answer_for_the_task(login, homework_name, task_id)
        correct_answer = self.database.get_right_answer_for_the_task(homework_name, task_id)
        if answer is None or correct_answer is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.", markup=self.__get_markup(message.chat.id))
            return

        if self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Правильный ответ на задание " + str(task_id) + ": " + correct_answer + "\nОтвет " + login + " на задание: " + answer, markup=self.__get_markup(message.chat.id))
        else:
            self.__send_message(message.chat.id, "Правильный ответ на задание " + str(task_id) + ": " + correct_answer + "\nВаш ответ на задание: " + answer, markup=self.__get_markup(message.chat.id))

    def __compute_callback_show_password(self, data, message):
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.", markup=self.__get_markup(message.chat.id))
            return

        login = data[0]
        user = self.database.get_user_by_login(login)
        if user is None:
            self.__send_message(message.chat.id, "Выбранный пользователь был удалён.", markup=self.__get_markup(message.chat.id))
            return

        if login != self.database.get_user_by_telegram_id(message.chat.id).login and not self.__is_super_admin(message.chat.id) and not user.status == constants.USER:
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.", markup=self.__get_markup(message.chat.id))
            return

        self.__send_message(message.chat.id, "Пароль пользователя \'" + login + "\': " + user.password, markup=self.__get_markup(message.chat.id))

    def __compute_callback_refresh_results_table(self, data, message):
        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        homework_name, first_task_id = data[0], int(data[1])
        homework = self.database.get_homework_by_name(homework_name)
        if homework is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.", markup=self.__get_markup(message.chat.id))
            return

        markup = markups.get_results_table(self.database.get_results(constants.USER, homework_name), homework_name, len(homework.right_answers), first_task_id)
        try:
            self.client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=message.text, reply_markup=markup)
        except:
            self.__send_message(message.chat.id, "Информация актуальна.", markup=self.__get_markup(message.chat.id))

    def __compute_callback_describe_exercise(self, data, message):
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.", markup=self.__get_markup(message.chat.id))
            return

        homework_name = data[0]
        homework = self.database.get_homework_by_name(homework_name)
        if homework is None:
            self.__send_message(message.chat.id, "Выбранное задание было удалено.", markup=self.__get_markup(message.chat.id))
            return

        text = "Всего задач " + str(len(homework.right_answers)) + ". Правильные ответы:\n"
        for i in range(len(homework.right_answers)):
            text += str(i + 1) + ": " + homework.right_answers[i] + "\n"
        self.__send_message(message.chat.id, text, markup=self.__get_markup(message.chat.id))

    def __compute_callback_change_results_table(self, data, message):
        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованны.", markup=self.__get_markup(message.chat.id))
            return

        homework_name, first_task_id = data[0], int(data[1])
        homework = self.database.get_homework_by_name(homework_name)
        if homework is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.", markup=self.__get_markup(message.chat.id))
            return

        markup = markups.get_results_table(self.database.get_results(constants.USER, homework_name), homework_name, len(homework.right_answers), first_task_id)
        try:
            self.client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=message.text, reply_markup=markup)
        except:
            pass

    def __compute_keyboard_back(self, message):
        self.wait_mode[message.chat.id] = None
        self.__send_message(message.chat.id, "Выход выполнен.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_sign_up(self, message):
        if self.database.get_user_by_telegram_id(message.chat.id) is not None:
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
            if self.database.get_user_by_login(login) is None:
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
        if self.database.get_user_by_login(login).password != password:
            self.__send_message(message.chat.id, "Введённый неправильный пароль, авторизация отменена.",
                                markup=self.__get_markup(message.chat.id))
            return

        id = self.__get_id_by_login(login)
        self.database.change_user_telegram_id(login, message.chat.id)
        if id is not None:
            self.__send_message(id, "В ваш профиль выполнен вход с другого телеграм аккаунта, вы были разлогинены.", markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Успешная авторизация!", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_sign_out(self, message):
        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        self.database.change_user_telegram_id(user.login, constants.UNAUTHORIZED_TELEGRAM_ID)
        self.__send_message(message.chat.id, "Вы вышли из аккаунта.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add_account(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_account, status="WAIT_LOGIN")
            self.__send_message(message.chat.id, "Введите логин для нового аккаунта:", markup=self.__get_markup(message.chat.id))
            return

        if self.wait_mode[message.chat.id].status == "WAIT_LOGIN":
            login = message.text
            if self.database.get_user_by_login(login) is not None:
                self.wait_mode[message.chat.id] = None
                self.__send_message(message.chat.id, "Введённый логин уже существует, создание аккаунта отменено.", markup=self.__get_markup(message.chat.id))
                return

            if login.count("$") > 0 or not self.__check_name(login):
                self.wait_mode[message.chat.id] = None
                self.__send_message(message.chat.id, "Логин содержит запрещённые символы, создание аккаунта отменено.", markup=self.__get_markup(message.chat.id))
                return

            if len(login) > constants.MAX_LOGIN_SIZE:
                self.wait_mode[message.chat.id] = None
                self.__send_message(message.chat.id, "Введённый логин слишком длинный, создание аккаунта отменено.", markup=self.__get_markup(message.chat.id))
                return

            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_account, data=login)
            self.__send_message(message.chat.id, "Введите пароль для нового аккаунта:", markup=self.__get_markup(message.chat.id))
            return

        login = self.wait_mode[message.chat.id].data
        password = message.text
        self.wait_mode[message.chat.id] = None

        self.database.add_user(User(login, password, constants.USER, constants.UNAUTHORIZED_TELEGRAM_ID))
        self.__send_message(message.chat.id, "Аккаунт успешно создан.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete_account(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete_account)
            self.__send_message(message.chat.id, "Введите логин аккаунта для удаления:", markup=self.__get_markup(message.chat.id))
            return

        login = message.text
        self.wait_mode[message.chat.id] = None
        if self.database.get_user_by_login(login) is None:
            self.__send_message(message.chat.id, "Введённый логин не существует, удаление аккаунта отменено.", markup=self.__get_markup(message.chat.id))
            return

        status = self.database.get_user_by_login(login).status
        if status == constants.SUPER_ADMIN or not self.__is_super_admin(message.chat.id) and status == constants.ADMIN:
            self.__send_message(message.chat.id, "Вы не можете удалить этот аккаунт.", markup=self.__get_markup(message.chat.id))
            return

        id = self.__get_id_by_login(login)
        self.database.delete_user_by_login(login)
        if id is not None:
            self.__send_message(id, "Ваш аккаунт был удалён.", markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Аккаунт успешно удалён.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add_admin(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_admin)
            self.__send_message(message.chat.id, "Введите логин аккаунта для выдачи прав администратора:", markup=self.__get_markup(message.chat.id))
            return

        login = message.text
        user = self.database.get_user_by_login(login)
        self.wait_mode[message.chat.id] = None
        if user is None:
            self.__send_message(message.chat.id, "Введённый логин не существует, модификация прав отменена.", markup=self.__get_markup(message.chat.id))
            return

        if user.status == constants.SUPER_ADMIN or user.status == constants.ADMIN:
            self.__send_message(message.chat.id, "Пользователь уже обладает правами администратора, модификация прав отменена.", markup=self.__get_markup(message.chat.id))
            return

        self.database.change_user_status(login, constants.ADMIN)
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
        if self.database.get_user_by_login(login) is None:
            self.__send_message(message.chat.id, "Введённый логин не существует, модификация прав отменена.", markup=self.__get_markup(message.chat.id))
            return

        if self.database.get_user_by_login(login).status == constants.SUPER_ADMIN:
            self.__send_message(message.chat.id, "Запрещено менять права доступа этого пользователя.", markup=self.__get_markup(message.chat.id))
            return

        self.database.change_user_status(login, constants.USER)
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
            if homework_name.count("$") > 0 or not self.__check_name(homework_name):
                self.wait_mode[message.chat.id] = None
                self.__send_message(message.chat.id, "Имя домашней работы содержит запрещённые символы, создание задания отменено.", markup=self.__get_markup(message.chat.id))
                return

            if len(homework_name) > constants.MAX_HOMEWORK_NAME_SIZE:
                self.wait_mode[message.chat.id] = None
                self.__send_message(message.chat.id, "Имя домашней работы слишком длинное, создание задания отменено.", markup=self.__get_markup(message.chat.id))
                return

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

        self.database.add_homework(Homework(homework_name, answers))
        self.__send_message(message.chat.id, "Задание успешно добавленно.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete_exercise(self, message):
        if self.wait_mode[message.chat.id] is None:
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete_exercise)
            self.__send_message(message.chat.id, "Введите имя задания для удаления.", markup=self.__get_markup(message.chat.id))
            return

        homework_name = message.text
        homework = self.database.get_homework_by_name(homework_name)
        self.wait_mode[message.chat.id] = None
        if homework is None:
            self.__send_message(message.chat.id, "Задания с введённым именем не существует, удаление отменено.", markup=self.__get_markup(message.chat.id))
            return

        self.database.delete_homework_by_name(homework_name)
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

    def __compute_keyboard_get_results(self, message):
        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        markup = markups.get_all_homeworks(self.database.get_all_homeworks_names(), "C")
        if markup is None:
            self.__send_message(message.chat.id, "На данный момент нет открытых работ.", markup=markup)
        else:
            self.__send_message(message.chat.id, "Выберите имя работы.", markup=markup)

    def __compute_keyboard_get_list_of_logins(self, message):
        if self.__is_super_admin(message.chat.id):
            users = self.database.get_all_users_with_status(constants.SUPER_ADMIN)
            if len(users) > 0:
                self.__send_message(message.chat.id, "Супер-администраторы:", markup=self.__get_markup(message.chat.id))
                for user in users:
                    markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text="Показать пароль", callback_data="F" + user.login)]])
                    self.__send_message(message.chat.id, user.login, markup=markup)

        users = self.database.get_all_users_with_status(constants.ADMIN)
        if len(users) > 0:
            self.__send_message(message.chat.id, "Администраторы:", markup=self.__get_markup(message.chat.id))
            for user in users:
                markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text="Показать пароль", callback_data="F" + user.login)]])
                self.__send_message(message.chat.id, user.login, markup=markup)

        users = self.database.get_all_users_with_status(constants.USER)
        if len(users) > 0:
            self.__send_message(message.chat.id, "Ученики:", markup=self.__get_markup(message.chat.id))
            for user in users:
                markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text="Показать пароль", callback_data="F" + user.login)]])
                self.__send_message(message.chat.id, user.login, markup=markup)

    def __compute_keyboard_get_list_of_exercises(self, message):
        homework_names = self.database.get_all_homeworks_names()
        if len(homework_names) > 0:
            for name in homework_names:
                markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text="Результаты", callback_data="C" + name), types.InlineKeyboardButton(text="Описание", callback_data="H" + name)]])
                self.__send_message(message.chat.id, name, markup=markup)
        else:
            self.__send_message(message.chat.id, "На данный момент нет открытых работ.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_send_answer(self, message):
        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        markup = markups.get_all_homeworks(self.database.get_all_homeworks_names(), "A")
        if markup is None:
            self.__send_message(message.chat.id, "На данный момент для вас нет открытых задач.", markup=markup)
        else:
            self.__send_message(message.chat.id, "Выберите имя работы.", markup=markup)

    def __handler(self):
        print("TG client started.")

        @self.client.message_handler(commands=['start'])
        def start(message):
            self.__compute_command_start(message)

        @self.client.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            self.client.answer_callback_query(callback_query_id=call.id)
            callback_type = call.data[0]
            data = call.data[1:].split("$")

            if callback_type == "0":  # NONE
                return

            if callback_type == "A":  # SELECT_HOMEWORK
                self.__compute_callback_select_homework(data, call.message)
            elif callback_type == "B":  # SELECT_TASK
                self.__compute_callback_select_task(data, call.message)
            elif callback_type == "C":  # SHOW_HOMEWORK
                self.__compute_callback_show_homework(data, call.message)
            elif callback_type == "D":  # SHOW_TASK
                self.__compute_callback_show_task(data, call.message)
            elif callback_type == "E":  # SHOW_TASK_IN_TABLE
                self.__compute_callback_show_task_in_table(data, call.message)
            elif callback_type == "F":  # SHOW_PASSWORD
                self.__compute_callback_show_password(data, call.message)
            elif callback_type == "G":  # REFRESH_RESULTS_TABLE
                self.__compute_callback_refresh_results_table(data, call.message)
            elif callback_type == "H":  # DESCRIBE_EXERCISE
                self.__compute_callback_describe_exercise(data, call.message)
            elif callback_type == "I":  # CHANGE_RESULTS_TABLE
                self.__compute_callback_change_results_table(data, call.message)
            else:
                add_error_to_log("Unknown callback: " + callback_type)

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
            elif message.text == "Вывести результаты":
                self.__compute_keyboard_get_results(message)
            elif message.text == "Список аккаунтов" and self.__is_admin(message.chat.id):
                self.__compute_keyboard_get_list_of_logins(message)
            elif message.text == "Список заданий" and self.__is_admin(message.chat.id):
                self.__compute_keyboard_get_list_of_exercises(message)
            else:
                self.__send_message(message.chat.id, "Неизвестная команда.")

        self.client.infinity_polling()

    def run(self):
        self.client = TeleBot(config.TELEGRAM_TOKEN)
        self.__handler()
