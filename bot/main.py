import locale
from telegram_logic.user_handler import UserHandler


def main():
    locale.setlocale(locale.LC_ALL, locale.normalize("RU"))

    bot = UserHandler()
    bot.run()


if __name__ == "__main__":
    main()
    #
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
    # def __handler(self) -> None:
    #     @self.client.callback_query_handler(func=lambda call: True)
    #     def callback_inline(call):
    #         elif callback_type == "F":  # SHOW_PASSWORD
    #             self.__compute_callback_show_password(data, call.message)
    #         elif callback_type == "H":  # DESCRIBE_EXERCISE
    #             self.__compute_callback_describe_exercise(data, call.message)
    #         elif callback_type == "K":  # GET_CURRENT_USER_ON_LOGIN
    #             self.__compute_callback_get_current_user_on_login(data, call.message)
    #         elif callback_type == "L":  # GET_USER_RESULTS
    #             self.__compute_callback_get_user_results(data, call.message)