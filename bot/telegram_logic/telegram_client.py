from telebot import types, TeleBot
from bot.user import User
from bot.homework import Homework
from bot.database.database_funcs import DatabaseHelper
from bot.telegram_logic import markups
from bot.config import TELEGRAM_TOKEN
from bot import constants


def add_error_to_log(text: str) -> None:
    error_log = open(constants.ERROR_LOG_NAME, "a")
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

    def __check_name(self, name: str) -> bool:
        # Check login/homework name, returns True if all ASCII codes are good
        for symbol in name:
            if ord(symbol) >= 123:
                return False
        return True

    def __check_task(self, login: str, homework_name: str, task_id: int):
        user = self.database.get_user_by_login(login)

        # If there is no such user just return None
        if user is None:
            return None

        user_answer = self.database.get_user_answer_for_the_task(login, homework_name, task_id)

        # If user did not give any answers just return None
        if user_answer is None or user_answer == '':
            return None

        # Returns True if user answer is right
        return self.database.get_right_answer_for_the_task(homework_name, task_id) == user_answer

    def __is_super_admin(self, id: int) -> bool:
        user = self.database.get_user_by_telegram_id(id)

        # Returns True if user exists and his status is SUPER_ADMIN
        return user is not None and user.status == constants.SUPER_ADMIN_STATUS

    def __is_admin(self, id: int) -> bool:
        user = self.database.get_user_by_telegram_id(id)

        # Returns True if user exists and his status is ADMIN or SUPER_ADMIN
        return user is not None and (user.status == constants.ADMIN_STATUS or user.status == constants.SUPER_ADMIN_STATUS)

    def __is_student(self, id: int) -> bool:
        user = self.database.get_user_by_telegram_id(id)

        # Returns True if user exists and his status is STUDENT
        return user is not None and user.status == constants.STUDENT_STATUS

    def __get_login_by_id(self, id: int):
        user = self.database.get_user_by_telegram_id(id)

        # If there is no such user just return None
        if user is None:
            return None

        return user.login

    def __get_id_by_login(self, login: str):
        user = self.database.get_user_by_login(login)

        # If there is no such user send error to error log
        if user is None:
            add_error_to_log("Invalid login in function __get_id_by_login")
            return None

        # If no one is logged in this account just return None
        if user.telegram_id == constants.UNAUTHORIZED_TELEGRAM_ID:
            return None

        return user.telegram_id

    def __get_markup(self, id: int):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Buttons description on bottom bar

        # Buttons in case when waiting input from user
        if id in self.wait_mode and self.wait_mode[id] is not None:
            if self.wait_mode[id].status == "ADD" or self.wait_mode[id].status == "DELETE":
                if self.__is_admin(id):
                    if self.wait_mode[id].status == "ADD":
                        markup.add(types.KeyboardButton(text="Ученик"))  # Add new student account
                    else:
                        markup.add(types.KeyboardButton(text="Аккаунт"))  # Delete exists account

                if self.__is_super_admin(id) and self.wait_mode[id].status == "ADD":
                    markup.add(types.KeyboardButton(text="Администратор"))  # Add new admin account

                if self.__is_admin(id):
                    markup.add(types.KeyboardButton(text="Задание"))  # Action with exercise

            # Default waiting-mode button
            markup.add(types.KeyboardButton(text="Назад"))  # Go back from input waiting
            return markup

        # Buttons in case when user is not authorized
        if self.database.get_user_by_telegram_id(id) is None:
            markup.add(types.KeyboardButton(text="Авторизоваться"))  # Authorize to existing account
            return markup

        # Buttons in the normal situation
        if self.__is_admin(id):
            # Buttons for admins
            markup.add(types.KeyboardButton(text="Добавить"),
                       types.KeyboardButton(text="Удалить"))  # Buttons for select action type
            markup.add(types.KeyboardButton(text="Вывести результаты"))  # Show results table
            markup.add(types.KeyboardButton(text="Список аккаунтов"))  # Show accounts list
            markup.add(types.KeyboardButton(text="Список заданий"))  # Show exercises list
        else:
            # Buttons for users
            markup.add(types.KeyboardButton(text="Сдать задачу"))  # Solve unsolved exercise
            markup.add(types.KeyboardButton(text="Вывести результаты"))  # Show results table

        # Default buttons for authorized users
        markup.add(types.KeyboardButton(text="Статус"))  # Get login, password and status of current account
        markup.add(types.KeyboardButton(text="Выйти"))  # Exit from current account
        return markup

    def __send_message(self, id: int, text: str, markup=None) -> None:
        # If markup is None send just text
        if markup is None:
            self.client.send_message(id, text=text)
        else:
            self.client.send_message(id, text=text, reply_markup=markup)

    def __compute_command_start(self, message) -> None:
        # This function is called on command '/start'

        text = "С возвращением!"
        if self.database.get_user_by_telegram_id(message.chat.id) is None:
            text = "Пожалуйста, авторизуйтесь."

        # Send hello phrase and update keyboard
        self.__send_message(message.chat.id, text, markup=self.__get_markup(message.chat.id))

    def __compute_wait_answer(self, message) -> None:
        # This function is called on user input during waiting answer on some exercise

        homework_name = self.wait_mode[message.chat.id].data["homework_name"]  # Getting stored current homework name
        task_id = self.wait_mode[message.chat.id].data["task_id"]  # Getting stored current task id
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        # If user is not student, reject answer
        if not self.__is_student(message.chat.id):
            self.__send_message(message.chat.id, "Сдача задания невозможна.", markup=self.__get_markup(message.chat.id))
            return

        user = self.database.get_user_by_telegram_id(message.chat.id)
        homework = self.database.get_homework_by_name(homework_name)

        # If homework was blocked or deleted, reject answer
        if homework is None or homework.grade != user.grade:
            self.__send_message(message.chat.id, "Выбранная работа недоступна.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If task was blocked or deleted, reject answer
        if self.__check_task(user.login, homework_name, task_id) is not None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.",
                                markup=self.__get_markup(message.chat.id))
            return

        answer = message.text

        # Empty answer are banned
        if answer == '':
            self.__send_message(message.chat.id, "Введён некорректный ответ, сдача задания отменена.",
                                markup=self.__get_markup(message.chat.id))
            return

        correct_answer = self.database.send_answer_for_the_task(user.login, homework_name, task_id, answer)
        if answer == correct_answer:
            result = "✅"
            self.__send_message(message.chat.id, "Ваш ответ правильный!", markup=self.__get_markup(message.chat.id))
        else:
            result = "❌"
            self.__send_message(message.chat.id, "Ваш ответ неправильный. Правильный ответ: " + correct_answer,
                                markup=self.__get_markup(message.chat.id))

        # Sending notifications to all admins
        for admin in self.database.get_all_users_with_status(constants.ADMIN_STATUS) + self.database.get_all_users_with_status(
                constants.SUPER_ADMIN_STATUS):
            id = self.__get_id_by_login(admin.login)

            # Scip all not authorized admins
            if id is None:
                continue

            self.__send_message(id, user.login + " добавил ответ к заданию " + str(
                task_id) + " в работе \'" + homework_name + "\'\nПравильный ответ: " + correct_answer + "\nОтвет ученика: " + answer + "\nРезультат: " + result,
                                markup=self.__get_markup(id))

    def __compute_wait_student_password(self, message) -> None:
        # This function is called on admin input during waiting password for create new student account

        login = self.wait_mode[message.chat.id].data["login"]  # Getting stored current login
        grade = self.wait_mode[message.chat.id].data["grade"]  # Getting stored current grade
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
                                markup=self.__get_markup(message.chat.id))
            return

        password = message.text

        self.database.add_user(User(login, password, constants.STUDENT_STATUS, constants.UNAUTHORIZED_TELEGRAM_ID, grade))  # Creating new user
        self.__send_message(message.chat.id, "Аккаунт студента успешно создан.", markup=self.__get_markup(message.chat.id))

    def __compute_wait_add_new_exercise(self, message) -> None:
        # This function is called on admin input during waiting number of tasks or value of right answers for create new exercise

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None  # Drop waiting mode
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the first call of this function (waiting input number of tasks)
        if self.wait_mode[message.chat.id].status == "WAIT_NUMBER_OF_EXERCISES":
            # Try to extract number of tasks from the message text
            success = True
            number = 0
            try:
                number = int(message.text)
            except:
                success = False

            # If number of tasks is incorrect or not positive, stop creating
            if not success or number <= 0:
                self.wait_mode[message.chat.id] = None  # Drop waiting mode
                self.__send_message(message.chat.id, "Введено некорректное число задач, создание задания отменено.",
                                    markup=self.__get_markup(message.chat.id))
                return

            # Start waiting right answer for each task (WaitModeDescription status is description of input state, exercise name and right answers saved in WaitModeDescription data)
            self.wait_mode[message.chat.id].status = {"current_number": 0, "amount": number}

        # If already taken exercise name and number of tasks

        # Waiting right answer starts when current_number > 0 and stop when current_number == amount
        if self.wait_mode[message.chat.id].status["current_number"] > 0:
            self.wait_mode[message.chat.id].data["answers"].append(
                message.text)  # Add right answer to WaitModeDescription data
            self.__send_message(message.chat.id, "Ответ принят.", markup=self.__get_markup(message.chat.id))

        if self.wait_mode[message.chat.id].status["current_number"] < self.wait_mode[message.chat.id].status["amount"]:
            self.wait_mode[message.chat.id].status["current_number"] += 1  # Update number of given answers
            self.__send_message(message.chat.id, "Введите ответ к задаче номер " + str(
                self.wait_mode[message.chat.id].status["current_number"]) + ":",
                                markup=self.__get_markup(message.chat.id))
            return

        homework_name = self.wait_mode[message.chat.id].data["name"]  # Getting stored exercise name
        grade = self.wait_mode[message.chat.id].data["grade"]  # Getting stored exercise grade
        answers = self.wait_mode[message.chat.id].data["answers"]  # Getting stored right answers for each task
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        self.database.add_homework(Homework(homework_name, grade, answers))  # Add new exercise
        self.__send_message(message.chat.id, "Задание успешно добавленно.", markup=self.__get_markup(message.chat.id))

    def __compute_callback_select_homework(self, data: list[str], message) -> None:
        # This function is called when user chooses homework for solve (in list of homeworks)

        # If user is not student, reject choice
        if not self.__is_student(message.chat.id):
            self.__send_message(message.chat.id, "Выбор задания невозможен.", markup=self.__get_markup(message.chat.id))
            return

        user = self.database.get_user_by_telegram_id(message.chat.id)
        homework_name = data[0]  # Getting chooses homework name
        homework = self.database.get_homework_by_name(homework_name)

        # If homework was blocked or deleted, reject choice
        if homework is None or homework.grade != user.grade:
            self.__send_message(message.chat.id, "Выбранная работа недоступна.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Creating table of tasks
        markup = markups.get_task_list(user.login, len(homework.right_answers), homework.name, self.__check_task)
        self.__send_message(message.chat.id, "Выберите задание.", markup=markup)

    def __compute_callback_select_task(self, data: list[str], message) -> None:
        # This function is called when user chooses task for solve (in list of tasks)

        # If user is not student, reject choice
        if not self.__is_student(message.chat.id):
            self.__send_message(message.chat.id, "Выбор задания невозможен.", markup=self.__get_markup(message.chat.id))
            return

        user = self.database.get_user_by_telegram_id(message.chat.id)
        homework_name, task_id = data[0], int(data[1])  # Getting chooses homework name and task id
        homework = self.database.get_homework_by_name(homework_name)

        # If homework was blocked or deleted, reject choice
        if homework is None or homework.grade != user.grade:
            self.__send_message(message.chat.id, "Выбранная работа недоступна.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Update table of tasks
        markup = markups.get_task_list(user.login, len(homework.right_answers), homework.name, self.__check_task)
        try:
            self.client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=message.text,
                                          reply_markup=markup)
        except:
            pass

        # If task was blocked or deleted, reject choice
        if self.__check_task(user.login, homework_name, task_id) is not None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Start waiting of answer for current task in current homework (they saved in WaitModeDescription.data)
        self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_wait_answer,
                                                              data={"homework_name": homework_name, "task_id": task_id})
        self.__send_message(message.chat.id, "Введите ответ на задание " + str(task_id) + ":",
                            markup=self.__get_markup(message.chat.id))

    def __compute_callback_show_homework(self, data: list[str], message) -> None:
        # This function is called when user chooses homework for show results (in list of homeworks)

        user = self.database.get_user_by_telegram_id(message.chat.id)

        # If user is not authorized, reject choice
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
            return

        homework_name = data[0]
        homework = self.database.get_homework_by_name(homework_name)

        # If homework was blocked or deleted, reject choice
        if homework is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Creating table of results
        markup = markups.get_results_table(self.database.get_results(constants.STUDENT_STATUS, homework_name), homework_name,
                                           len(homework.right_answers), 1)
        self.__send_message(message.chat.id, "Текущие результаты по работе \'" + homework_name + "\', " + str(homework.grade) + " класс:", markup=markup)

    def __compute_callback_show_task(self, data: list[str], message) -> None:
        # This function is called when user chooses task for see right answer on this task (in list of tasks)

        # If user is not student, reject choice
        if not self.__is_student(message.chat.id):
            self.__send_message(message.chat.id, "Просмотр задания невозможен.",
                                markup=self.__get_markup(message.chat.id))
            return

        user = self.database.get_user_by_telegram_id(message.chat.id)
        homework_name, task_id = data[0], int(data[1])  # Getting chooses homework name and task id
        homework = self.database.get_homework_by_name(homework_name)

        # If homework was blocked or deleted, reject choice
        if homework is None or homework.grade != user.grade:
            self.__send_message(message.chat.id, "Выбранная работа недоступна.",
                                markup=self.__get_markup(message.chat.id))
            return

        answer = self.database.get_user_answer_for_the_task(user.login, homework_name,
                                                            task_id)  # Getting user answer on current task
        correct_answer = self.database.get_right_answer_for_the_task(homework_name, task_id)

        # If task was blocked or deleted, reject choice
        if answer is None or correct_answer is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Compare answers and show right answer
        if answer != correct_answer:
            self.__send_message(message.chat.id, "Ваш ответ: " + answer + "\nПравильный ответ: " + correct_answer,
                                markup=self.__get_markup(message.chat.id))
        else:
            self.__send_message(message.chat.id, "Ваш правильный ответ: " + answer,
                                markup=self.__get_markup(message.chat.id))

    def __compute_callback_show_task_in_table(self, data: list[str], message) -> None:
        # This function is called when user chooses task for see right answer on this task (in results table)

        user = self.database.get_user_by_telegram_id(message.chat.id)

        # If user is not authorized, reject choice
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
            return

        login, homework_name, task_id = data[0], data[1], int(
            data[2])  # Getting chooses user login, homework name and task id

        # If user is not admin, and he want to see someone else's answer, reject choice
        if not self.__is_admin(message.chat.id) and login != user.login:
            return

        answer = self.database.get_user_answer_for_the_task(login, homework_name,
                                                            task_id)  # Getting user answer on current task
        correct_answer = self.database.get_right_answer_for_the_task(homework_name, task_id)

        # If task was blocked or deleted, reject choice
        if answer is None or correct_answer is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Show right answer
        if self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Правильный ответ на задание " + str(
                task_id) + ": " + correct_answer + "\nОтвет \'" + login + "\' на задание: " + answer,
                                markup=self.__get_markup(message.chat.id))
        else:
            self.__send_message(message.chat.id, "Правильный ответ на задание " + str(
                task_id) + ": " + correct_answer + "\nВаш ответ на задание: " + answer,
                                markup=self.__get_markup(message.chat.id))

    def __compute_callback_show_password(self, data: list[str], message) -> None:
        # This function is called when admin chooses some user for see his password (in list of logins)

        # If user is not admin, reject choice
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
                                markup=self.__get_markup(message.chat.id))
            return

        login = data[0]  # Getting chooses user login
        user = self.database.get_user_by_login(login)

        # If current user was deleted, reject choice
        if user is None:
            self.__send_message(message.chat.id, "Выбранный пользователь был удалён.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Not super-admin can not see passwords of other admins
        if login != self.database.get_user_by_telegram_id(message.chat.id).login and not self.__is_super_admin(
                message.chat.id) and not user.status == constants.STUDENT_STATUS:
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Show user password
        self.__send_message(message.chat.id, "Пароль пользователя \'" + login + "\': " + user.password,
                            markup=self.__get_markup(message.chat.id))

    def __compute_callback_refresh_results_table(self, data: list[str], message) -> None:
        # This function is called when user wants to refresh results table

        user = self.database.get_user_by_telegram_id(message.chat.id)

        # If user is not authorized, reject attempt
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
            return

        homework_name, first_task_id = data[0], int(data[1])  # Getting chooses homework name and last first task id
        homework = self.database.get_homework_by_name(homework_name)

        # If homework was blocked or deleted, reject choice
        if homework is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Update results table
        markup = markups.get_results_table(self.database.get_results(constants.STUDENT_STATUS, homework_name), homework_name,
                                           len(homework.right_answers), first_task_id)
        try:
            self.client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=message.text,
                                          reply_markup=markup)
        except:
            # Table already updated
            self.__send_message(message.chat.id, "Информация актуальна.", markup=self.__get_markup(message.chat.id))

    def __compute_callback_describe_exercise(self, data: list[str], message) -> None:
        # This function is called when admin chooses some exercise for see its description (in list of exercises)

        # If user is not admin, reject choice
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
                                markup=self.__get_markup(message.chat.id))
            return

        homework_name = data[0]  # Getting chooses homework name
        homework = self.database.get_homework_by_name(homework_name)

        # If homework was blocked or deleted, reject choice
        if homework is None:
            self.__send_message(message.chat.id, "Выбранное задание было удалено.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Create and send description of current task
        text = "Класс работы: " + str(homework.grade) + "\nВсего задач: " + str(len(homework.right_answers)) + "\nПравильные ответы:\n"
        for i in range(len(homework.right_answers)):
            text += str(i + 1) + ": " + homework.right_answers[i] + "\n"
        self.__send_message(message.chat.id, text, markup=self.__get_markup(message.chat.id))

    def __compute_callback_change_results_table(self, data: list[str], message) -> None:
        # This function is called when user wants to switch page in results table

        user = self.database.get_user_by_telegram_id(message.chat.id)

        # If user is not authorized, reject attempt
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
            return

        homework_name, first_task_id = data[0], int(data[1])  # Getting chooses homework name and new first task id
        homework = self.database.get_homework_by_name(homework_name)

        # If homework was blocked or deleted, reject choice
        if homework is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Update results table
        markup = markups.get_results_table(self.database.get_results(constants.STUDENT_STATUS, homework_name), homework_name,
                                           len(homework.right_answers), first_task_id)
        try:
            self.client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=message.text,
                                          reply_markup=markup)
        except:
            pass

    def __compute_callback_get_user_statistic_in_table(self, data: list[str], message) -> None:
        # This function is called when user wants to see statistic of one user in results table

        user = self.database.get_user_by_telegram_id(message.chat.id)

        # If user is not authorized, reject command
        if user is None:
            self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
            return

        login, homework_name = data[0], data[1]  # Getting chooses login and homework name
        homework = self.database.get_homework_by_name(homework_name)

        # If homework was blocked or deleted, reject choice
        if homework is None:
            self.__send_message(message.chat.id, "Выбранное задание недоступно.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Calculation number of right solved tasks
        tasks_number = len(homework.right_answers)
        solved_tasks_number = 0
        for i in range(1, tasks_number + 1):
            solved_tasks_number += self.database.get_user_answer_for_the_task(login, homework_name, i) == \
                                   homework.right_answers[i - 1]

        # Send statistic
        self.__send_message(message.chat.id,
                            login + "\nРешено " + str(solved_tasks_number) + " / " + str(tasks_number) + " задач.",
                            markup=self.__get_markup(message.chat.id))

    def __compute_callback_get_current_user_on_login(self, data: list[str], message) -> None:
        # This function is called when admin wants to see current user on chooses login (in list of logins)

        # If user is not admin, reject choice
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
                                markup=self.__get_markup(message.chat.id))
            return

        login = data[0]  # Getting chooses user login
        user = self.database.get_user_by_login(login)

        # If current user was deleted, reject choice
        if user is None:
            self.__send_message(message.chat.id, "Выбранный пользователь был удалён.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If there is no user on chooses login
        if user.telegram_id == constants.UNAUTHORIZED_TELEGRAM_ID:
            self.__send_message(message.chat.id, "В этот аккаунт никто не вошёл.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Show user telegram info
        info = self.client.get_chat_member(user.telegram_id, user.telegram_id).user
        self.__send_message(message.chat.id, "Имя: " + info.first_name + "\nФамилия: " + info.last_name + "\nХэндл: @" + info.username, markup=self.__get_markup(message.chat.id))

    def __compute_callback_get_user_results(self, data: list[str], message) -> None:
        # This function is called when admin wants to see results of chooses user (in list of logins)

        # If user is not admin, reject choice
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
                                markup=self.__get_markup(message.chat.id))
            return

        login = data[0]  # Getting chooses user login
        user = self.database.get_user_by_login(login)

        # If current user was deleted, reject choice
        if user is None:
            self.__send_message(message.chat.id, "Выбранный пользователь был удалён.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Calculate user results
        user_results = []  # List of pairs (solved tasks number, tasks number)
        homeworks_names = self.database.get_all_homeworks_names()
        for homework_name in homeworks_names:
            homework = self.database.get_homework_by_name(homework_name)
            tasks_number = len(homework.right_answers)

            # Calculate solved tasks number in current homework
            solved_tasks_number = 0
            for i in range(1, tasks_number + 1):
                solved_tasks_number += self.database.get_user_answer_for_the_task(login, homework_name, i) == homework.right_answers[i - 1]

            user_results.append((solved_tasks_number, tasks_number))

        # Create table of user results and send results
        markup = markups.get_user_results_table(homeworks_names, user_results)
        self.__send_message(message.chat.id, "Результаты \'" + login + "\':", markup)

    def __compute_callback_add_student(self, data: list[str], message) -> None:
        # This function is called when admin chooses grade of new student (in list of grades)

        # If user is not admin, reject choice
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
                                markup=self.__get_markup(message.chat.id))
            return

        login, grade = data[0], int(data[1])  # Getting chooses user login and grade

        # Start waiting of password for create account with current login and grade (login and grade saved in WaitModeDescription data)
        self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_wait_student_password, data={"login": login, "grade": grade})
        self.__send_message(message.chat.id, "Введите пароль для нового аккаунта:", markup=self.__get_markup(message.chat.id))

    def __compute_callback_add_exercise(self, data: list[str], message) -> None:
        # This function is called when admin chooses grade for new exercise (in list of grades)

        # If user is not admin, reject choice
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
                                markup=self.__get_markup(message.chat.id))
            return

        homework_name, grade = data[0], int(data[1])  # Getting chooses exercise name and grade of exercise

        # Start waiting of number of tasks for create new exercise (WaitModeDescription status is WAIT_NUMBER_OF_EXERCISES, exercise name and grade saved in WaitModeDescription data)
        self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_wait_add_new_exercise, data={"name": homework_name, "grade": grade, "answers": []}, status="WAIT_NUMBER_OF_EXERCISES")
        self.__send_message(message.chat.id, "Введите количество заданий:", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_back(self, message) -> None:
        # This function is called when user wants to stop waiting input

        self.wait_mode[message.chat.id] = None  # Drop waiting mode
        self.__send_message(message.chat.id, "Выход выполнен.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_get_state(self, message) -> None:
        # This function is called when user wants to see his login, password and status

        user = self.database.get_user_by_telegram_id(message.chat.id)

        # If user is not authorized, reject command
        if user is None:
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # Compute user description
        description = "Логин: " + user.login + "\nПароль: " + user.password + "\nСтатус: " + user.status
        if self.__is_student(message.chat.id):
            description += "\nКласс: " + str(user.grade)

        # Send login, password and status
        self.__send_message(message.chat.id, description, markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_sign_up(self, message) -> None:
        # This function is called when user wants to authorize

        user = self.database.get_user_by_telegram_id(message.chat.id)

        # If user already authorized, reject command
        if user is not None:
            self.wait_mode[message.chat.id] = None  # Drop waiting mode
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # If it is the first call of this function
        if self.wait_mode[message.chat.id] is None:
            # Start waiting of login for authorizing (WaitModeDescription status is WAIT_LOGIN)
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_sign_up, status="WAIT_LOGIN")
            self.__send_message(message.chat.id, "Введите логин аккаунта для авторизации:",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the second call of this function (waiting input login)
        if self.wait_mode[message.chat.id].status == "WAIT_LOGIN":
            login = message.text

            # If there is no such login, stop authorization
            if self.database.get_user_by_login(login) is None:
                self.wait_mode[message.chat.id] = None  # Drop waiting mode
                self.__send_message(message.chat.id, "Введённый логин не существует, авторизация отменена.",
                                    markup=self.__get_markup(message.chat.id))
                return

            # Start waiting of password for authorizing in current login (login saved in WaitModeDescription data)
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_sign_up, data=login)
            self.__send_message(message.chat.id, "Введите пароль:", markup=self.__get_markup(message.chat.id))
            return

        # If it is the third call of this function (waiting input login)
        login = self.wait_mode[message.chat.id].data  # Getting stored current login
        password = message.text
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        # If password is incorrect, stop authorization
        if self.database.get_user_by_login(login).password != password:
            self.__send_message(message.chat.id, "Введён неправильный пароль, авторизация отменена.",
                                markup=self.__get_markup(message.chat.id))
            return

        id = self.__get_id_by_login(login)  # Getting last user on current login
        self.database.change_user_telegram_id(login, message.chat.id)  # Authorize current user

        # Send notification for last user on current login if he exists
        if id is not None:
            self.wait_mode[id] = None  # Drop waiting mode
            self.__send_message(id, "В ваш профиль выполнен вход с другого телеграм аккаунта, вы были разлогинены.",
                                markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Успешная авторизация!", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_sign_out(self, message) -> None:
        # This function is called when user wants to sign out from current account

        user = self.database.get_user_by_telegram_id(message.chat.id)

        # If user is not authorized, reject command
        if user is None:
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        self.database.change_user_telegram_id(user.login, constants.UNAUTHORIZED_TELEGRAM_ID)  # Sign out current user
        self.__send_message(message.chat.id, "Вы вышли из аккаунта.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add_student(self, message) -> None:
        # This function is called when admin wants to create new account

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None  # Drop waiting mode
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # If it is the first call of this function
        if self.wait_mode[message.chat.id] is None:
            # Start waiting of login for creating new account
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_student)
            self.__send_message(message.chat.id,
                                "Введите логин для нового аккаунта (доступны латинские символы, цифры и знаки препинания):",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the second call of this function (waiting input login)
        login = message.text
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        # If login already exists, stop creating
        if self.database.get_user_by_login(login) is not None:
            self.__send_message(message.chat.id, "Введённый логин уже существует, создание аккаунта отменено.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If login is incorrect, stop creating
        if login.count("$") > 0 or not self.__check_name(login):
            self.__send_message(message.chat.id, "Логин содержит запрещённые символы, создание аккаунта отменено.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If login too long, stop creating
        if len(login) > constants.MAX_LOGIN_SIZE:
            self.__send_message(message.chat.id, "Введённый логин слишком длинный, создание аккаунта отменено.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Create list of grades
        markup = markups.get_list_of_grades(login, "M")
        self.__send_message(message.chat.id, "Выберите класс нового ученика.", markup=markup)

    def __compute_keyboard_add_admin(self, message) -> None:
        # This function is called when admin wants to create new admin account

        # If user is not super admin, reject command
        if not self.__is_super_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None  # Drop waiting mode
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # If it is the first call of this function
        if self.wait_mode[message.chat.id] is None:
            # Start waiting of login for creating new account (WaitModeDescription status is WAIT_LOGIN)
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_admin,
                                                                  status="WAIT_LOGIN")
            self.__send_message(message.chat.id,
                                "Введите логин для нового аккаунта администратора (доступны латинские символы, цифры и знаки препинания):",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the second call of this function (waiting input login)
        if self.wait_mode[message.chat.id].status == "WAIT_LOGIN":
            login = message.text

            # If login already exists, stop creating
            if self.database.get_user_by_login(login) is not None:
                self.wait_mode[message.chat.id] = None  # Drop waiting mode
                self.__send_message(message.chat.id, "Введённый логин уже существует, создание аккаунта отменено.",
                                    markup=self.__get_markup(message.chat.id))
                return

            # If login is incorrect, stop creating
            if login.count("$") > 0 or not self.__check_name(login):
                self.wait_mode[message.chat.id] = None  # Drop waiting mode
                self.__send_message(message.chat.id, "Логин содержит запрещённые символы, создание аккаунта отменено.",
                                    markup=self.__get_markup(message.chat.id))
                return

            # If login too long, stop creating
            if len(login) > constants.MAX_LOGIN_SIZE:
                self.wait_mode[message.chat.id] = None  # Drop waiting mode
                self.__send_message(message.chat.id, "Введённый логин слишком длинный, создание аккаунта отменено.",
                                    markup=self.__get_markup(message.chat.id))
                return

            # Start waiting of password for create account with current login (login saved in WaitModeDescription data)
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_admin, data=login)
            self.__send_message(message.chat.id, "Введите пароль для нового аккаунта администратора:",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the third call of this function (waiting input password)
        login = self.wait_mode[message.chat.id].data  # Getting stored current login
        password = message.text
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        self.database.add_user(User(login, password, constants.ADMIN_STATUS, constants.UNAUTHORIZED_TELEGRAM_ID))  # Creating new admin account
        self.__send_message(message.chat.id, "Аккаунт администратора успешно создан.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete_account(self, message) -> None:
        # This function is called when admin wants to delete existing account

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None  # Drop waiting mode
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # If it is the first call of this function
        if self.wait_mode[message.chat.id] is None:
            # Start waiting of login for deleting account
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete_account)
            self.__send_message(message.chat.id, "Введите логин аккаунта для удаления:",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the second call of this function (waiting input login)
        login = message.text
        user = self.database.get_user_by_login(login)
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        # If there is no such login, stop deleting
        if user is None:
            self.__send_message(message.chat.id, "Введённый логин не существует, удаление аккаунта отменено.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Admin can delete only users accounts
        if user.status == constants.SUPER_ADMIN_STATUS or not self.__is_super_admin(
                message.chat.id) and user.status == constants.ADMIN_STATUS:
            self.__send_message(message.chat.id, "Вы не можете удалить этот аккаунт.",
                                markup=self.__get_markup(message.chat.id))
            return

        id = self.__get_id_by_login(login)  # Getting id of last user on current account
        self.database.delete_user_by_login(login)  # Deleting account

        # Send notification to last user if he exists
        if id is not None:
            self.wait_mode[id] = None  # Drop waiting mode
            self.__send_message(id, "Ваш аккаунт был удалён.", markup=self.__get_markup(id))

        self.__send_message(message.chat.id, "Аккаунт успешно удалён.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add_exercise(self, message) -> None:
        # This function is called when admin wants to add new exercise

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None  # Drop waiting mode
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # If it is the first call of this function
        if self.wait_mode[message.chat.id] is None:
            # Start waiting of name for create new exercise
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_exercise)
            self.__send_message(message.chat.id,
                                "Введите имя нового задания (доступны латинские символы, цифры и знаки препинания):",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the second call of this function (waiting input exercise name)
        homework_name = message.text
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        # If exercise with same name already exists, stop creating
        if self.database.get_homework_by_name(homework_name) is not None:
            self.__send_message(message.chat.id, "Работа с таким именем уже существует, создание задания отменено.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If exercise name is incorrect, stop creating
        if homework_name.count("$") > 0 or not self.__check_name(homework_name):
            self.__send_message(message.chat.id,
                                "Имя домашней работы содержит запрещённые символы, создание задания отменено.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If exercise name too long, stop creating
        if len(homework_name) > constants.MAX_HOMEWORK_NAME_SIZE:
            self.__send_message(message.chat.id, "Имя домашней работы слишком длинное, создание задания отменено.",
                                markup=self.__get_markup(message.chat.id))
            return

        # Create list of grades
        markup = markups.get_list_of_grades(homework_name, "N")
        self.__send_message(message.chat.id, "Выберите для какого класса будет доступно новое задание.", markup=markup)

    def __compute_keyboard_delete_exercise(self, message) -> None:
        # This function is called when admin wants to delete exercise

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None  # Drop waiting mode
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # If it is the first call of this function
        if self.wait_mode[message.chat.id] is None:
            # Start waiting of name for delete exercise
            self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete_exercise)
            self.__send_message(message.chat.id, "Введите имя задания для удаления.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the second call of this function (waiting input exercise name)
        homework_name = message.text
        homework = self.database.get_homework_by_name(homework_name)
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        # If there is no such exercise, stop deleting
        if homework is None:
            self.__send_message(message.chat.id, "Задания с введённым именем не существует, удаление отменено.",
                                markup=self.__get_markup(message.chat.id))
            return

        self.database.delete_homework_by_name(homework_name)  # Delete exercise
        self.__send_message(message.chat.id, "Задание успешно удалено.", markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_add(self, message) -> None:
        # This function is called when admin wants to add something

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None  # Drop waiting mode
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # If it is the first call of this function
        if self.wait_mode[message.chat.id] is None:
            # Start waiting of action type (WaitModeDescription status describe action class (ADD/DELETE))
            if self.__is_super_admin(message.chat.id):
                self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add, status="ADD")
            else:
                self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add, status="ADD")

            self.__send_message(message.chat.id, "Выберите объект модификации.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the second call of this function (waiting input action type)
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        # Finding value of current action type
        if message.text == "Ученик":  # Add new account
            self.__compute_keyboard_add_student(message)
        elif message.text == "Администратор":  # Add new account
            self.__compute_keyboard_add_admin(message)
        elif message.text == "Задание":  # Add new exercise
            self.__compute_keyboard_add_exercise(message)
        else:  # Unknown command type
            self.__send_message(message.chat.id, "Неизвестная команда, отмена модификации.",
                                markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_delete(self, message) -> None:
        # This function is called when admin wants to delete something

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.wait_mode[message.chat.id] = None  # Drop waiting mode
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # If it is the first call of this function
        if self.wait_mode[message.chat.id] is None:
            # Start waiting of action type (WaitModeDescription status describe action class (ADD/DELETE))
            if self.__is_super_admin(message.chat.id):
                self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete, status="DELETE")
            else:
                self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_delete, status="DELETE")

            self.__send_message(message.chat.id, "Выберите объект модификации.",
                                markup=self.__get_markup(message.chat.id))
            return

        # If it is the second call of this function (waiting input action type)
        self.wait_mode[message.chat.id] = None  # Drop waiting mode

        # Finding value of current action type
        if message.text == "Аккаунт":  # Delete existing account
            self.__compute_keyboard_delete_account(message)
        elif message.text == "Задание":  # Delete existing exercise
            self.__compute_keyboard_delete_exercise(message)
        else:  # Unknown command type
            self.__send_message(message.chat.id, "Неизвестная команда, отмена модификации.",
                                markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_get_results(self, message) -> None:
        # This function is called when user wants to see results table

        # If user is not authorized, reject command
        user = self.database.get_user_by_telegram_id(message.chat.id)
        if user is None:
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # Create homeworks list (user must choose homework name for see results table of it)
        markup = markups.get_all_homeworks(self.database.get_all_homeworks_names(), "C")
        if markup is None:
            # There is no homeworks created
            self.__send_message(message.chat.id, "На данный момент нет открытых работ.", markup=markup)
        else:
            self.__send_message(message.chat.id, "Выберите имя работы.", markup=markup)

    def __compute_keyboard_get_list_of_logins(self, message) -> None:
        # This function is called when admin wants to see list of accounts

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        # Admins can see only other admins and users (not super-admins)
        if self.__is_super_admin(message.chat.id):
            users = self.database.get_all_users_with_status(constants.SUPER_ADMIN_STATUS)
            if len(users) > 0:
                # Send list of super-admins
                self.__send_message(message.chat.id, "Супер-администраторы:", markup=self.__get_markup(message.chat.id))
                for user in users:
                    # Create buttons under login
                    markup = types.InlineKeyboardMarkup(
                        [[types.InlineKeyboardButton(text="Пароль", callback_data="F" + user.login),
                          types.InlineKeyboardButton(text="Пользователь", callback_data="K" + user.login)]])
                    self.__send_message(message.chat.id, user.login, markup=markup)

        users = self.database.get_all_users_with_status(constants.ADMIN_STATUS)
        if len(users) > 0:
            # Send list of admins
            self.__send_message(message.chat.id, "Администраторы:", markup=self.__get_markup(message.chat.id))
            for user in users:
                # Create buttons under login
                markup = types.InlineKeyboardMarkup(
                    [[types.InlineKeyboardButton(text="Пароль", callback_data="F" + user.login),
                      types.InlineKeyboardButton(text="Пользователь", callback_data="K" + user.login)]])
                self.__send_message(message.chat.id, user.login, markup=markup)

        users = self.database.get_all_users_with_status(constants.STUDENT_STATUS)
        if len(users) > 0:
            # Send list of users
            self.__send_message(message.chat.id, "Ученики:", markup=self.__get_markup(message.chat.id))
            for user in users:
                # Create buttons under login
                markup = types.InlineKeyboardMarkup(
                    [[types.InlineKeyboardButton(text="Пароль", callback_data="F" + user.login),
                      types.InlineKeyboardButton(text="Пользователь", callback_data="K" + user.login),
                      types.InlineKeyboardButton(text="Результаты", callback_data="L" + user.login)]])
                self.__send_message(message.chat.id, user.login + ", " + str(user.grade) + " класс", markup=markup)

    def __compute_keyboard_get_list_of_exercises(self, message) -> None:
        # This function is called when admin wants to see list of exercises

        # If user is not admin, reject command
        if not self.__is_admin(message.chat.id):
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        homework_names = self.database.get_all_homeworks_names()
        if len(homework_names) > 0:
            # Send list of homeworks
            for name in homework_names:
                # Create buttons under homework name
                markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text="Результаты",
                                                                                 callback_data="C" + name),
                                                      types.InlineKeyboardButton(text="Описание",
                                                                                 callback_data="H" + name)]])
                self.__send_message(message.chat.id, name, markup=markup)
        else:
            # There is no homeworks created
            self.__send_message(message.chat.id, "На данный момент нет открытых работ.",
                                markup=self.__get_markup(message.chat.id))

    def __compute_keyboard_send_answer(self, message) -> None:
        # This function is called when user wants to send answer on some task

        # If user is not student, reject command
        if not self.__is_student(message.chat.id):
            self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
            return

        user = self.database.get_user_by_telegram_id(message.chat.id)

        # Create list of homeworks
        markup = markups.get_all_homeworks(self.database.get_all_homeworks_names_for_grade(user.grade), "A")
        if markup is None:
            # There is no homeworks created
            self.__send_message(message.chat.id, "На данный момент для вас нет открытых задач.", markup=markup)
        else:
            self.__send_message(message.chat.id, "Выберите имя работы.", markup=markup)

    def __handler(self) -> None:
        # This function is called on all events

        print("TG client started.")

        @self.client.message_handler(commands=['start'])
        def start(message):
            self.__compute_command_start(message)

        @self.client.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            # Computing callback from inline button

            self.client.answer_callback_query(
                callback_query_id=call.id)  # Answer on callback (required to continue working with the button)
            callback_type = call.data[0]  # Special type of pressed button
            data = call.data[1:].split("$")

            # NONE - type of empty button
            if callback_type == "0":  # NONE
                return

            # Drop current waiting mode if button was pressed
            if call.message.chat.id in self.wait_mode and self.wait_mode[call.message.chat.id] is not None:
                self.__compute_keyboard_back(call.message)

            # Finding value of current action type
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
            elif callback_type == "J":  # GET_USER_STATISTIC_IN_TABLE
                self.__compute_callback_get_user_statistic_in_table(data, call.message)
            elif callback_type == "K":  # GET_CURRENT_USER_ON_LOGIN
                self.__compute_callback_get_current_user_on_login(data, call.message)
            elif callback_type == "L":  # GET_USER_RESULTS
                self.__compute_callback_get_user_results(data, call.message)
            elif callback_type == "M":  # ADD_STUDENT
                self.__compute_callback_add_student(data, call.message)
            elif callback_type == "N":  # ADD_EXERCISE
                self.__compute_callback_add_exercise(data, call.message)
            else:  # Unknown action type
                add_error_to_log("Unknown callback: " + callback_type)

        @self.client.message_handler(content_types=["text"])
        def on_message(message):
            # Computing user input (from keyboard)

            # Skip all message from chats
            if message.chat.id != message.from_user.id:
                return

            # Add wait mode to user
            if message.chat.id not in self.wait_mode:
                self.wait_mode[message.chat.id] = None  # Drop waiting mode

            # If waiting mode is active, compute it
            if self.wait_mode[message.chat.id] is not None:
                if message.text == "Назад":  # Go back from wait mode
                    self.__compute_keyboard_back(message)
                else:  # Compute wait mode
                    self.wait_mode[message.chat.id].function(message)
            elif message.text == "Авторизоваться":  # Authorize to existing account
                self.__compute_keyboard_sign_up(message)
            elif message.text == "Статус":  # Get login, password and status of current account
                self.__compute_keyboard_get_state(message)
            elif message.text == "Выйти":  # Exit from current account
                self.__compute_keyboard_sign_out(message)
            elif message.text == "Сдать задачу":  # Solve unsolved exercise
                self.__compute_keyboard_send_answer(message)
            elif message.text == "Добавить":  # Action add something
                self.__compute_keyboard_add(message)
            elif message.text == "Удалить":  # Action delete something
                self.__compute_keyboard_delete(message)
            elif message.text == "Вывести результаты":  # Show results table
                self.__compute_keyboard_get_results(message)
            elif message.text == "Список аккаунтов":  # Show accounts list
                self.__compute_keyboard_get_list_of_logins(message)
            elif message.text == "Список заданий":  # Show exercises list
                self.__compute_keyboard_get_list_of_exercises(message)
            else:  # Unknown keyboard command
                self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))

        self.client.infinity_polling()  # Launch bot

    def run(self) -> None:
        # This function launch bot

        self.client = TeleBot(TELEGRAM_TOKEN)  # Create telebot client object
        self.__handler()  # Launch bot
