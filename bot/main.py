import locale
from telegram_logic.user_handler import UserHandler


def main():
    locale.setlocale(locale.LC_ALL, locale.normalize("RU"))

    bot = UserHandler()
    bot.run()


if __name__ == "__main__":
    main()

    # def __check_task(self, login: str, homework_name: str, task_id: int):
    #     user = self.database.get_user_by_login(login)
    #
    #     # If there is no such user just return None
    #     if user is None:
    #         return None
    #
    #     user_answer = self.database.get_user_answer_for_the_task(login, homework_name, task_id)
    #
    #     # If user did not give any answers just return None
    #     if user_answer is None or user_answer == '':
    #         return None
    #
    #     # Returns True if user answer is right
    #     return self.database.get_right_answer_for_the_task(homework_name, task_id) == user_answer
    #
    # def __compute_wait_answer(self, message) -> None:
    #     # This function is called on user input during waiting answer on some exercise
    #
    #     homework_name = self.wait_mode[message.chat.id].data["homework_name"]  # Getting stored current homework name
    #     task_id = self.wait_mode[message.chat.id].data["task_id"]  # Getting stored current task id
    #     self.wait_mode[message.chat.id] = None  # Drop waiting mode
    #
    #     # If user is not student, reject answer
    #     if not self.__is_student(message.chat.id):
    #         self.__send_message(message.chat.id, "Сдача задания невозможна.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     user = self.database.get_user_by_telegram_id(message.chat.id)
    #     homework = self.database.get_homework_by_name(homework_name)
    #
    #     # If homework was blocked or deleted, reject answer
    #     if homework is None or homework.grade != user.grade:
    #         self.__send_message(message.chat.id, "Выбранная работа недоступна.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If task was blocked or deleted, reject answer
    #     if self.__check_task(user.login, homework_name, task_id) is not None:
    #         self.__send_message(message.chat.id, "Выбранное задание недоступно.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     answer = message.text
    #
    #     # Empty answer are banned
    #     if answer == '':
    #         self.__send_message(message.chat.id, "Введён некорректный ответ, сдача задания отменена.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     correct_answer = self.database.send_answer_for_the_task(user.login, homework_name, task_id, answer)
    #     if answer == correct_answer:
    #         result = "✅"
    #         self.__send_message(message.chat.id, "Ваш ответ правильный!", markup=self.__get_markup(message.chat.id))
    #     else:
    #         result = "❌"
    #         self.__send_message(message.chat.id, "Ваш ответ неправильный. Правильный ответ: " + correct_answer,
    #                             markup=self.__get_markup(message.chat.id))
    #
    #     # Sending notifications to all admins
    #     for admin in self.database.get_all_users_with_status(
    #             constants.ADMIN_STATUS) + self.database.get_all_users_with_status(
    #             constants.SUPER_ADMIN_STATUS):
    #         id = self.__get_id_by_login(admin.login)
    #
    #         # Scip all not authorized admins
    #         if id is None:
    #             continue
    #
    #         self.__send_message(id, user.login + ", " + str(user.grade) + " класс добавил ответ к заданию " + str(
    #             task_id) + " в работе \'" + homework_name + "\'\nПравильный ответ: " + correct_answer + "\nОтвет ученика: " + answer + "\nРезультат: " + result,
    #                             markup=self.__get_markup(id))
    #
    # def __compute_wait_student_password(self, message) -> None:
    #     # This function is called on admin input during waiting password for create new student account
    #
    #     login = self.wait_mode[message.chat.id].data["login"]  # Getting stored current login
    #     grade = self.wait_mode[message.chat.id].data["grade"]  # Getting stored current grade
    #     self.wait_mode[message.chat.id] = None  # Drop waiting mode
    #
    #     # If user is not admin, reject command
    #     if not self.__is_admin(message.chat.id):
    #         self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     password = message.text
    #
    #     self.database.add_user(User(login, password, constants.STUDENT_STATUS, constants.UNAUTHORIZED_TELEGRAM_ID,
    #                                 grade))  # Creating new user
    #     self.__send_message(message.chat.id, "Аккаунт студента успешно создан.",
    #                         markup=self.__get_markup(message.chat.id))
    #
    # def __compute_wait_add_new_exercise(self, message) -> None:
    #     # This function is called on admin input during waiting number of tasks or value of right answers for create new exercise
    #
    #     # If user is not admin, reject command
    #     if not self.__is_admin(message.chat.id):
    #         self.wait_mode[message.chat.id] = None  # Drop waiting mode
    #         self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If it is the first call of this function (waiting input number of tasks)
    #     if self.wait_mode[message.chat.id].status == "WAIT_NUMBER_OF_EXERCISES":
    #         # Try to extract number of tasks from the message text
    #         success = True
    #         number = 0
    #         try:
    #             number = int(message.text)
    #         except:
    #             success = False
    #
    #         # If number of tasks is incorrect or not positive, stop creating
    #         if not success or number <= 0:
    #             self.wait_mode[message.chat.id] = None  # Drop waiting mode
    #             self.__send_message(message.chat.id, "Введено некорректное число задач, создание задания отменено.",
    #                                 markup=self.__get_markup(message.chat.id))
    #             return
    #
    #         # Start waiting right answer for each task (WaitModeDescription status is description of input state, exercise name and right answers saved in WaitModeDescription data)
    #         self.wait_mode[message.chat.id].status = {"current_number": 0, "amount": number}
    #
    #     # If already taken exercise name and number of tasks
    #
    #     # Waiting right answer starts when current_number > 0 and stop when current_number == amount
    #     if self.wait_mode[message.chat.id].status["current_number"] > 0:
    #         self.wait_mode[message.chat.id].data["answers"].append(
    #             message.text)  # Add right answer to WaitModeDescription data
    #         self.__send_message(message.chat.id, "Ответ принят.", markup=self.__get_markup(message.chat.id))
    #
    #     if self.wait_mode[message.chat.id].status["current_number"] < self.wait_mode[message.chat.id].status["amount"]:
    #         self.wait_mode[message.chat.id].status["current_number"] += 1  # Update number of given answers
    #         self.__send_message(message.chat.id, "Введите ответ к задаче номер " + str(
    #             self.wait_mode[message.chat.id].status["current_number"]) + ":",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     homework_name = self.wait_mode[message.chat.id].data["name"]  # Getting stored exercise name
    #     grade = self.wait_mode[message.chat.id].data["grade"]  # Getting stored exercise grade
    #     answers = self.wait_mode[message.chat.id].data["answers"]  # Getting stored right answers for each task
    #     self.wait_mode[message.chat.id] = None  # Drop waiting mode
    #
    #     self.database.add_homework(Homework(homework_name, grade, answers))  # Add new exercise
    #     self.__send_message(message.chat.id, "Задание успешно добавленно.", markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_select_homework(self, data: list[str], message) -> None:
    #     # This function is called when user chooses homework for solve (in list of homeworks)
    #
    #     # If user is not student, reject choice
    #     if not self.__is_student(message.chat.id):
    #         self.__send_message(message.chat.id, "Выбор задания невозможен.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     user = self.database.get_user_by_telegram_id(message.chat.id)
    #     homework_name = data[0]  # Getting chooses homework name
    #     homework = self.database.get_homework_by_name(homework_name)
    #
    #     # If homework was blocked or deleted, reject choice
    #     if homework is None or homework.grade != user.grade:
    #         self.__send_message(message.chat.id, "Выбранная работа недоступна.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Creating table of tasks
    #     markup = markups.get_task_list(user.login, len(homework.right_answers), homework.name, self.__check_task)
    #     self.__send_message(message.chat.id, "Выберите задание.", markup=markup)
    #
    # def __compute_callback_select_task(self, data: list[str], message) -> None:
    #     # This function is called when user chooses task for solve (in list of tasks)
    #
    #     # If user is not student, reject choice
    #     if not self.__is_student(message.chat.id):
    #         self.__send_message(message.chat.id, "Выбор задания невозможен.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     user = self.database.get_user_by_telegram_id(message.chat.id)
    #     homework_name, task_id = data[0], int(data[1])  # Getting chooses homework name and task id
    #     homework = self.database.get_homework_by_name(homework_name)
    #
    #     # If homework was blocked or deleted, reject choice
    #     if homework is None or homework.grade != user.grade:
    #         self.__send_message(message.chat.id, "Выбранная работа недоступна.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Update table of tasks
    #     markup = markups.get_task_list(user.login, len(homework.right_answers), homework.name, self.__check_task)
    #     try:
    #         self.client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=message.text,
    #                                       reply_markup=markup)
    #     except:
    #         pass
    #
    #     # If task was blocked or deleted, reject choice
    #     if self.__check_task(user.login, homework_name, task_id) is not None:
    #         self.__send_message(message.chat.id, "Выбранное задание недоступно.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Start waiting of answer for current task in current homework (they saved in WaitModeDescription.data)
    #     self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_wait_answer,
    #                                                           data={"homework_name": homework_name, "task_id": task_id})
    #     self.__send_message(message.chat.id, "Введите ответ на задание " + str(task_id) + ":",
    #                         markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_show_homework(self, data: list[str], message) -> None:
    #     # This function is called when user chooses homework for show results (in list of homeworks)
    #
    #     user = self.database.get_user_by_telegram_id(message.chat.id)
    #
    #     # If user is not authorized, reject choice
    #     if user is None:
    #         self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     homework_name = data[0]
    #     homework = self.database.get_homework_by_name(homework_name)
    #
    #     # If homework was blocked or deleted, reject choice
    #     if homework is None:
    #         self.__send_message(message.chat.id, "Выбранное задание недоступно.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Creating table of results
    #     markup = markups.get_results_table(self.database.get_results(constants.STUDENT_STATUS, homework_name),
    #                                        homework_name,
    #                                        len(homework.right_answers), 1)
    #     self.__send_message(message.chat.id, "Текущие результаты по работе \'" + homework_name + "\', " + str(
    #         homework.grade) + " класс:", markup=markup)
    #
    # def __compute_callback_show_task(self, data: list[str], message) -> None:
    #     # This function is called when user chooses task for see right answer on this task (in list of tasks)
    #
    #     # If user is not student, reject choice
    #     if not self.__is_student(message.chat.id):
    #         self.__send_message(message.chat.id, "Просмотр задания невозможен.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     user = self.database.get_user_by_telegram_id(message.chat.id)
    #     homework_name, task_id = data[0], int(data[1])  # Getting chooses homework name and task id
    #     homework = self.database.get_homework_by_name(homework_name)
    #
    #     # If homework was blocked or deleted, reject choice
    #     if homework is None or homework.grade != user.grade:
    #         self.__send_message(message.chat.id, "Выбранная работа недоступна.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     answer = self.database.get_user_answer_for_the_task(user.login, homework_name,
    #                                                         task_id)  # Getting user answer on current task
    #     correct_answer = self.database.get_right_answer_for_the_task(homework_name, task_id)
    #
    #     # If task was blocked or deleted, reject choice
    #     if answer is None or correct_answer is None:
    #         self.__send_message(message.chat.id, "Выбранное задание недоступно.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Compare answers and show right answer
    #     if answer != correct_answer:
    #         self.__send_message(message.chat.id, "Ваш ответ: " + answer + "\nПравильный ответ: " + correct_answer,
    #                             markup=self.__get_markup(message.chat.id))
    #     else:
    #         self.__send_message(message.chat.id, "Ваш правильный ответ: " + answer,
    #                             markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_show_task_in_table(self, data: list[str], message) -> None:
    #     # This function is called when user chooses task for see right answer on this task (in results table)
    #
    #     user = self.database.get_user_by_telegram_id(message.chat.id)
    #
    #     # If user is not authorized, reject choice
    #     if user is None:
    #         self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     login, homework_name, task_id = data[0], data[1], int(
    #         data[2])  # Getting chooses user login, homework name and task id
    #
    #     # If user is not admin, and he want to see someone else's answer, reject choice
    #     if not self.__is_admin(message.chat.id) and login != user.login:
    #         return
    #
    #     answer = self.database.get_user_answer_for_the_task(login, homework_name,
    #                                                         task_id)  # Getting user answer on current task
    #     correct_answer = self.database.get_right_answer_for_the_task(homework_name, task_id)
    #
    #     # If task was blocked or deleted, reject choice
    #     if answer is None or correct_answer is None:
    #         self.__send_message(message.chat.id, "Выбранное задание недоступно.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Show right answer
    #     if self.__is_admin(message.chat.id):
    #         self.__send_message(message.chat.id, "Правильный ответ на задание " + str(
    #             task_id) + ": " + correct_answer + "\nОтвет \'" + login + "\' на задание: " + answer,
    #                             markup=self.__get_markup(message.chat.id))
    #     else:
    #         self.__send_message(message.chat.id, "Правильный ответ на задание " + str(
    #             task_id) + ": " + correct_answer + "\nВаш ответ на задание: " + answer,
    #                             markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_show_password(self, data: list[str], message) -> None:
    #     # This function is called when admin chooses some user for see his password (in list of logins)
    #
    #     # If user is not admin, reject choice
    #     if not self.__is_admin(message.chat.id):
    #         self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     login = data[0]  # Getting chooses user login
    #     user = self.database.get_user_by_login(login)
    #
    #     # If current user was deleted, reject choice
    #     if user is None:
    #         self.__send_message(message.chat.id, "Выбранный пользователь был удалён.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Not super-admin can not see passwords of other admins
    #     if login != self.database.get_user_by_telegram_id(message.chat.id).login and not self.__is_super_admin(
    #             message.chat.id) and not user.status == constants.STUDENT_STATUS:
    #         self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Show user password
    #     self.__send_message(message.chat.id, "Пароль пользователя \'" + login + "\': " + user.password,
    #                         markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_refresh_results_table(self, data: list[str], message) -> None:
    #     # This function is called when user wants to refresh results table
    #
    #     user = self.database.get_user_by_telegram_id(message.chat.id)
    #
    #     # If user is not authorized, reject attempt
    #     if user is None:
    #         self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     homework_name, first_task_id = data[0], int(data[1])  # Getting chooses homework name and last first task id
    #     homework = self.database.get_homework_by_name(homework_name)
    #
    #     # If homework was blocked or deleted, reject choice
    #     if homework is None:
    #         self.__send_message(message.chat.id, "Выбранное задание недоступно.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Update results table
    #     markup = markups.get_results_table(self.database.get_results(constants.STUDENT_STATUS, homework_name),
    #                                        homework_name,
    #                                        len(homework.right_answers), first_task_id)
    #     try:
    #         self.client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=message.text,
    #                                       reply_markup=markup)
    #     except:
    #         # Table already updated
    #         self.__send_message(message.chat.id, "Информация актуальна.", markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_describe_exercise(self, data: list[str], message) -> None:
    #     # This function is called when admin chooses some exercise for see its description (in list of exercises)
    #
    #     # If user is not admin, reject choice
    #     if not self.__is_admin(message.chat.id):
    #         self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     homework_name = data[0]  # Getting chooses homework name
    #     homework = self.database.get_homework_by_name(homework_name)
    #
    #     # If homework was blocked or deleted, reject choice
    #     if homework is None:
    #         self.__send_message(message.chat.id, "Выбранное задание было удалено.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Create and send description of current task
    #     text = "Класс работы: " + str(homework.grade) + "\nВсего задач: " + str(
    #         len(homework.right_answers)) + "\nПравильные ответы:\n"
    #     for i in range(len(homework.right_answers)):
    #         text += str(i + 1) + ": " + homework.right_answers[i] + "\n"
    #     self.__send_message(message.chat.id, text, markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_change_results_table(self, data: list[str], message) -> None:
    #     # This function is called when user wants to switch page in results table
    #
    #     user = self.database.get_user_by_telegram_id(message.chat.id)
    #
    #     # If user is not authorized, reject attempt
    #     if user is None:
    #         self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     homework_name, first_task_id = data[0], int(data[1])  # Getting chooses homework name and new first task id
    #     homework = self.database.get_homework_by_name(homework_name)
    #
    #     # If homework was blocked or deleted, reject choice
    #     if homework is None:
    #         self.__send_message(message.chat.id, "Выбранное задание недоступно.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Update results table
    #     markup = markups.get_results_table(self.database.get_results(constants.STUDENT_STATUS, homework_name),
    #                                        homework_name,
    #                                        len(homework.right_answers), first_task_id)
    #     try:
    #         self.client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=message.text,
    #                                       reply_markup=markup)
    #     except:
    #         pass
    #
    # def __compute_callback_get_user_statistic_in_table(self, data: list[str], message) -> None:
    #     # This function is called when user wants to see statistic of one user in results table
    #
    #     user = self.database.get_user_by_telegram_id(message.chat.id)
    #
    #     # If user is not authorized, reject command
    #     if user is None:
    #         self.__send_message(message.chat.id, "Вы не авторизованы.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     login, homework_name = data[0], data[1]  # Getting chooses login and homework name
    #     homework = self.database.get_homework_by_name(homework_name)
    #
    #     # If homework was blocked or deleted, reject choice
    #     if homework is None:
    #         self.__send_message(message.chat.id, "Выбранное задание недоступно.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Calculation number of right solved tasks
    #     tasks_number = len(homework.right_answers)
    #     solved_tasks_number = 0
    #     for i in range(1, tasks_number + 1):
    #         solved_tasks_number += self.database.get_user_answer_for_the_task(login, homework_name, i) == \
    #                                homework.right_answers[i - 1]
    #
    #     # Send statistic
    #     self.__send_message(message.chat.id,
    #                         login + "\nРешено " + str(solved_tasks_number) + " / " + str(tasks_number) + " задач.",
    #                         markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_get_current_user_on_login(self, data: list[str], message) -> None:
    #     # This function is called when admin wants to see current user on chooses login (in list of logins)
    #
    #     # If user is not admin, reject choice
    #     if not self.__is_admin(message.chat.id):
    #         self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     login = data[0]  # Getting chooses user login
    #     user = self.database.get_user_by_login(login)
    #
    #     # If current user was deleted, reject choice
    #     if user is None:
    #         self.__send_message(message.chat.id, "Выбранный пользователь был удалён.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If there is no user on chooses login
    #     if user.telegram_id == constants.UNAUTHORIZED_TELEGRAM_ID:
    #         self.__send_message(message.chat.id, "В этот аккаунт никто не вошёл.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Show user telegram info
    #     info = self.client.get_chat_member(user.telegram_id, user.telegram_id).user
    #     self.__send_message(message.chat.id,
    #                         "Имя: " + info.first_name + "\nФамилия: " + info.last_name + "\nХэндл: @" + info.username,
    #                         markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_get_user_results(self, data: list[str], message) -> None:
    #     # This function is called when admin wants to see results of chooses user (in list of logins)
    #
    #     # If user is not admin, reject choice
    #     if not self.__is_admin(message.chat.id):
    #         self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     login = data[0]  # Getting chooses user login
    #     user = self.database.get_user_by_login(login)
    #
    #     # If current user was deleted, reject choice
    #     if user is None:
    #         self.__send_message(message.chat.id, "Выбранный пользователь был удалён.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Calculate user results
    #     user_results = []  # List of pairs (solved tasks number, tasks number)
    #     homeworks_names = self.database.get_all_homeworks_names()
    #     for homework_name in homeworks_names:
    #         homework = self.database.get_homework_by_name(homework_name)
    #         tasks_number = len(homework.right_answers)
    #
    #         # Calculate solved tasks number in current homework
    #         solved_tasks_number = 0
    #         for i in range(1, tasks_number + 1):
    #             solved_tasks_number += self.database.get_user_answer_for_the_task(login, homework_name, i) == \
    #                                    homework.right_answers[i - 1]
    #
    #         user_results.append((solved_tasks_number, tasks_number))
    #
    #     # Create table of user results and send results
    #     markup = markups.get_user_results_table(homeworks_names, user_results)
    #     self.__send_message(message.chat.id, "Результаты \'" + login + "\':", markup)
    #
    # def __compute_callback_add_student(self, data: list[str], message) -> None:
    #     # This function is called when admin chooses grade of new student (in list of grades)
    #
    #     # If user is not admin, reject choice
    #     if not self.__is_admin(message.chat.id):
    #         self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     login, grade = data[0], int(data[1])  # Getting chooses user login and grade
    #
    #     # Start waiting of password for create account with current login and grade (login and grade saved in WaitModeDescription data)
    #     self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_wait_student_password,
    #                                                           data={"login": login, "grade": grade})
    #     self.__send_message(message.chat.id, "Введите пароль для нового аккаунта:",
    #                         markup=self.__get_markup(message.chat.id))
    #
    # def __compute_callback_add_exercise(self, data: list[str], message) -> None:
    #     # This function is called when admin chooses grade for new exercise (in list of grades)
    #
    #     # If user is not admin, reject choice
    #     if not self.__is_admin(message.chat.id):
    #         self.__send_message(message.chat.id, "Вы не обладаете достаточными правами.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     homework_name, grade = data[0], int(data[1])  # Getting chooses exercise name and grade of exercise
    #
    #     # Start waiting of number of tasks for create new exercise (WaitModeDescription status is WAIT_NUMBER_OF_EXERCISES, exercise name and grade saved in WaitModeDescription data)
    #     self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_wait_add_new_exercise,
    #                                                           data={"name": homework_name, "grade": grade,
    #                                                                 "answers": []}, status="WAIT_NUMBER_OF_EXERCISES")
    #     self.__send_message(message.chat.id, "Введите количество заданий:", markup=self.__get_markup(message.chat.id))
    #
    # def __compute_keyboard_add_student(self, message) -> None:
    #     # This function is called when admin wants to create new account
    #
    #     # If user is not admin, reject command
    #     if not self.__is_admin(message.chat.id):
    #         self.wait_mode[message.chat.id] = None  # Drop waiting mode
    #         self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If it is the first call of this function
    #     if self.wait_mode[message.chat.id] is None:
    #         # Start waiting of login for creating new account
    #         self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_student)
    #         self.__send_message(message.chat.id,
    #                             "Введите логин для нового аккаунта (доступны латинские символы, цифры и знаки препинания):",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If it is the second call of this function (waiting input login)
    #     login = message.text
    #     self.wait_mode[message.chat.id] = None  # Drop waiting mode
    #
    #     # If login already exists, stop creating
    #     if self.database.get_user_by_login(login) is not None:
    #         self.__send_message(message.chat.id, "Введённый логин уже существует, создание аккаунта отменено.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If login is incorrect, stop creating
    #     if login.count("$") > 0 or not self.__check_name(login):
    #         self.__send_message(message.chat.id, "Логин содержит запрещённые символы, создание аккаунта отменено.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If login too long, stop creating
    #     if len(login) > constants.MAX_LOGIN_SIZE:
    #         self.__send_message(message.chat.id, "Введённый логин слишком длинный, создание аккаунта отменено.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Create list of grades
    #     markup = markups.get_list_of_grades(login, "M")
    #     self.__send_message(message.chat.id, "Выберите класс нового ученика.", markup=markup)
    #
    # def __compute_keyboard_add_exercise(self, message) -> None:
    #     # This function is called when admin wants to add new exercise
    #
    #     # If user is not admin, reject command
    #     if not self.__is_admin(message.chat.id):
    #         self.wait_mode[message.chat.id] = None  # Drop waiting mode
    #         self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If it is the first call of this function
    #     if self.wait_mode[message.chat.id] is None:
    #         # Start waiting of name for create new exercise
    #         self.wait_mode[message.chat.id] = WaitModeDescription(self.__compute_keyboard_add_exercise)
    #         self.__send_message(message.chat.id,
    #                             "Введите имя нового задания (доступны латинские символы, цифры и знаки препинания):",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If it is the second call of this function (waiting input exercise name)
    #     homework_name = message.text
    #     self.wait_mode[message.chat.id] = None  # Drop waiting mode
    #
    #     # If exercise with same name already exists, stop creating
    #     if self.database.get_homework_by_name(homework_name) is not None:
    #         self.__send_message(message.chat.id, "Работа с таким именем уже существует, создание задания отменено.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If exercise name is incorrect, stop creating
    #     if homework_name.count("$") > 0 or not self.__check_name(homework_name):
    #         self.__send_message(message.chat.id,
    #                             "Имя домашней работы содержит запрещённые символы, создание задания отменено.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # If exercise name too long, stop creating
    #     if len(homework_name) > constants.MAX_HOMEWORK_NAME_SIZE:
    #         self.__send_message(message.chat.id, "Имя домашней работы слишком длинное, создание задания отменено.",
    #                             markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Create list of grades
    #     markup = markups.get_list_of_grades(homework_name, "N")
    #     self.__send_message(message.chat.id, "Выберите для какого класса будет доступно новое задание.", markup=markup)
    #
    # def __compute_keyboard_get_list_of_logins(self, message) -> None:
    #     # This function is called when admin wants to see list of accounts
    #
    #     # If user is not admin, reject command
    #     if not self.__is_admin(message.chat.id):
    #         self.__send_message(message.chat.id, "Неизвестная команда.", markup=self.__get_markup(message.chat.id))
    #         return
    #
    #     # Admins can see only other admins and users (not super-admins)
    #     if self.__is_super_admin(message.chat.id):
    #         users = self.database.get_all_users_with_status(constants.SUPER_ADMIN_STATUS)
    #         if len(users) > 0:
    #             # Send list of super-admins
    #             self.__send_message(message.chat.id, "Супер-администраторы:", markup=self.__get_markup(message.chat.id))
    #             for user in users:
    #                 # Create buttons under login
    #                 markup = types.InlineKeyboardMarkup(
    #                     [[types.InlineKeyboardButton(text="Пароль", callback_data="F" + user.login),
    #                       types.InlineKeyboardButton(text="Пользователь", callback_data="K" + user.login)]])
    #                 self.__send_message(message.chat.id, user.login, markup=markup)
    #
    #     users = self.database.get_all_users_with_status(constants.ADMIN_STATUS)
    #     if len(users) > 0:
    #         # Send list of admins
    #         self.__send_message(message.chat.id, "Администраторы:", markup=self.__get_markup(message.chat.id))
    #         for user in users:
    #             # Create buttons under login
    #             markup = types.InlineKeyboardMarkup(
    #                 [[types.InlineKeyboardButton(text="Пароль", callback_data="F" + user.login),
    #                   types.InlineKeyboardButton(text="Пользователь", callback_data="K" + user.login)]])
    #             self.__send_message(message.chat.id, user.login, markup=markup)
    #
    #     users = self.database.get_all_users_with_status(constants.STUDENT_STATUS)
    #     if len(users) > 0:
    #         # Send list of users
    #         self.__send_message(message.chat.id, "Ученики:", markup=self.__get_markup(message.chat.id))
    #         for user in users:
    #             # Create buttons under login
    #             markup = types.InlineKeyboardMarkup(
    #                 [[types.InlineKeyboardButton(text="Пароль", callback_data="F" + user.login),
    #                   types.InlineKeyboardButton(text="Пользователь", callback_data="K" + user.login),
    #                   types.InlineKeyboardButton(text="Результаты", callback_data="L" + user.login)]])
    #             self.__send_message(message.chat.id, user.login + ", " + str(user.grade) + " класс", markup=markup)
    #
    # def __handler(self) -> None:
    #     # This function is called on all events
    #
    #     print("TG client started.")
    #
    #     @self.client.message_handler(commands=['start'])
    #     def start(message):
    #         self.__compute_command_start(message)
    #
    #     @self.client.callback_query_handler(func=lambda call: True)
    #     def callback_inline(call):
    #         # Computing callback from inline button
    #
    #         self.client.answer_callback_query(
    #             callback_query_id=call.id)  # Answer on callback (required to continue working with the button)
    #         callback_type = call.data[0]  # Special type of pressed button
    #         data = call.data[1:].split("$")
    #
    #         # NONE - type of empty button
    #         if callback_type == "0":  # NONE
    #             return
    #
    #         # Drop current waiting mode if button was pressed
    #         if call.message.chat.id in self.wait_mode and self.wait_mode[call.message.chat.id] is not None:
    #             self.__compute_keyboard_back(call.message)
    #
    #         # Finding value of current action type
    #         if callback_type == "A":  # SELECT_HOMEWORK
    #             self.__compute_callback_select_homework(data, call.message)
    #         elif callback_type == "B":  # SELECT_TASK
    #             self.__compute_callback_select_task(data, call.message)
    #         elif callback_type == "C":  # SHOW_HOMEWORK
    #             self.__compute_callback_show_homework(data, call.message)
    #         elif callback_type == "D":  # SHOW_TASK
    #             self.__compute_callback_show_task(data, call.message)
    #         elif callback_type == "E":  # SHOW_TASK_IN_TABLE
    #             self.__compute_callback_show_task_in_table(data, call.message)
    #         elif callback_type == "F":  # SHOW_PASSWORD
    #             self.__compute_callback_show_password(data, call.message)
    #         elif callback_type == "G":  # REFRESH_RESULTS_TABLE
    #             self.__compute_callback_refresh_results_table(data, call.message)
    #         elif callback_type == "H":  # DESCRIBE_EXERCISE
    #             self.__compute_callback_describe_exercise(data, call.message)
    #         elif callback_type == "I":  # CHANGE_RESULTS_TABLE
    #             self.__compute_callback_change_results_table(data, call.message)
    #         elif callback_type == "J":  # GET_USER_STATISTIC_IN_TABLE
    #             self.__compute_callback_get_user_statistic_in_table(data, call.message)
    #         elif callback_type == "K":  # GET_CURRENT_USER_ON_LOGIN
    #             self.__compute_callback_get_current_user_on_login(data, call.message)
    #         elif callback_type == "L":  # GET_USER_RESULTS
    #             self.__compute_callback_get_user_results(data, call.message)
    #         elif callback_type == "M":  # ADD_STUDENT
    #             self.__compute_callback_add_student(data, call.message)
    #         elif callback_type == "N":  # ADD_EXERCISE
    #             self.__compute_callback_add_exercise(data, call.message)
    #         else:  # Unknown action type
    #             add_error_to_log("Unknown callback: " + callback_type)