import sqlite3
from bot.entities.user import User
from bot.entities.homework import Homework
from bot.constants import SUPER_ADMIN_STATUS, SUPER_ADMIN_LOGIN, SUPER_ADMIN_PASSWORD, UNAUTHORIZED_TELEGRAM_ID, \
    ADMINS, ADMIN_STATUS
from json import dumps, loads


class DatabaseHelper:
    def __init__(self, path_to_database: str, database_name: str):
        self.database_path: str = path_to_database + database_name
        self.create_database()

    def __create_connection_and_cursor(self):
        # Returns connection and cursor to our database
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        # Activating ability to use foreign keys
        cur.execute("PRAGMA foreign_keys = ON")
        con.commit()

        return con, cur

    def create_database(self):
        con, cur = self.__create_connection_and_cursor()

        # USE ONLY WHEN CREATING NEW DATABASE

        # Creates database with particular tables and relationships between them

        # Creating table with info about the users
        cur.execute("CREATE TABLE IF NOT EXISTS users("
                    "user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "login TEXT NOT NULL UNIQUE,"
                    "password TEXT NOT NULL,"
                    "status TEXT NOT NULL,"
                    "telegram_id INTEGER NOT NULL,"
                    "grade INTEGER);")

        # Creating table with info about the homeworks
        cur.execute("CREATE TABLE IF NOT EXISTS homeworks("
                    "homework_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "homework_name TEXT NOT NULL,"
                    "grade INTEGER NOT NULL)")

        # Creating table with info about the tasks
        cur.execute("CREATE TABLE IF NOT EXISTS tasks("
                    "task_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "index_in_homework TEXT NOT NULL,"
                    "right_answers STRING NOT NULL,"
                    "text_statement STRING,"
                    "file_statement STRING,"
                    "homework_id INTEGER NOT NULL,"
                    "FOREIGN KEY (homework_id) REFERENCES homeworks (homework_id) ON DELETE CASCADE)")

        # Creating table with results of solving tasks by users
        cur.execute("CREATE TABLE IF NOT EXISTS results("
                    "user_id INTEGER NOT NULL,"
                    "task_id INTEGER NOT NULL,"
                    "text_answer TEXT NOT NULL,"
                    "file_answer STRING NOT NULL,"
                    "FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,"
                    "FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,"
                    "PRIMARY KEY (user_id, task_id))")

        # Creating super admin
        if self.get_user_by_login(SUPER_ADMIN_LOGIN) is None:
            super_admin_user = User(SUPER_ADMIN_LOGIN, SUPER_ADMIN_PASSWORD, SUPER_ADMIN_STATUS,
                                    UNAUTHORIZED_TELEGRAM_ID)
            self.add_user(super_admin_user)

        # Creating admins
        for admin_login, admin_password in ADMINS:
            if self.get_user_by_login(admin_login) is None:
                admin_user = User(admin_login, admin_password, ADMIN_STATUS, UNAUTHORIZED_TELEGRAM_ID)
                self.add_user(admin_user)

        # Saving changes
        con.commit()

    def add_user(self, user: User):
        # Creating new user with the given parameters

        # If we already have user with given login there should be an exception
        if self.get_user_by_login(user.login) is not None:
            raise RuntimeError

        con, cur = self.__create_connection_and_cursor()

        cur.execute("INSERT INTO users (login, password, status, telegram_id, grade) "
                    "VALUES (?, ?, ?, ?, ?)", (user.login, user.password, user.status, user.telegram_id, user.grade))
        con.commit()

    def get_user_by_login(self, login: str):
        con, cur = self.__create_connection_and_cursor()

        # Getting user with the given login

        cur.execute("SELECT login, password, status, telegram_id, grade, user_id "
                    "FROM users "
                    "WHERE login = ?", (login,))

        user_parameters = cur.fetchone()

        # If there is no such user just return None
        if user_parameters is None:
            return None

        # Returning user with the given parameters
        return User(*user_parameters)

    def get_user_id_by_login(self, login: str):
        con, cur = self.__create_connection_and_cursor()

        # Getting user id with the corresponding login

        cur.execute("SELECT user_id "
                    "FROM users "
                    "WHERE login = ?", (login,))

        user_id = cur.fetchone()

        # If there is no such user just return None
        if user_id is None:
            return None

        # Returning user id with the given parameters
        return user_id[0]

    def get_user_by_user_id(self, user_id: str):
        con, cur = self.__create_connection_and_cursor()

        # Getting user with the corresponding user id

        cur.execute("SELECT login, password, status, telegram_id, grade, user_id "
                    "FROM users "
                    "WHERE user_id = ?", (user_id,))

        user_data = cur.fetchone()

        # If there is no such user just return None
        if user_data is None:
            return None

        # Returning user login with the given parameters
        return User(*user_data)

    def get_user_by_telegram_id(self, telegram_id: int):
        con, cur = self.__create_connection_and_cursor()

        # Getting user with the given telegram_id

        cur.execute("SELECT login, password, status, telegram_id, grade, user_id "
                    "FROM users "
                    "WHERE telegram_id = ?", (telegram_id,))

        user_parameters = cur.fetchone()

        # If there is no such user just return None
        if user_parameters is None:
            return None

        # Returning user with the given parameters
        return User(*user_parameters)

    def change_user_status(self, login: str, new_status: str):
        con, cur = self.__create_connection_and_cursor()

        cur.execute("UPDATE users SET status = ? WHERE login = ?", (new_status, login))
        con.commit()

    def change_user_telegram_id(self, login: str, new_telegram_id: int):
        con, cur = self.__create_connection_and_cursor()

        cur.execute("UPDATE users SET telegram_id = ? WHERE login = ?", (new_telegram_id, login))
        con.commit()

    def delete_user_by_login(self, login: str):
        con, cur = self.__create_connection_and_cursor()

        cur.execute("DELETE FROM users WHERE login = ?", (login,))
        con.commit()

    def add_homework(self, homework: Homework):
        # Creating new homework with the given parameters

        # If there is already a homework with given name we should raise an exception
        if self.get_homework_by_name(homework.name) is not None:
            raise RuntimeError

        con, cur = self.__create_connection_and_cursor()

        # There is a line in the database for each task in the homework
        for i in range(len(homework.right_answers)):
            right_answer = homework.right_answers[i]
            cur.execute("INSERT INTO tasks (homework_name, task_number, right_answer, grade) "
                        "VALUES (?, ?, ?, ?)", (homework.name, i + 1, right_answer, homework.grade))

        con.commit()

    def delete_homework_by_name(self, homework_name: str):
        # Deletes all the tasks in the homework by its name

        con, cur = self.__create_connection_and_cursor()

        cur.execute("DELETE FROM tasks WHERE homework_name = ?", (homework_name,))
        con.commit()

    def get_task_id(self, homework_name: str, task_number: int):
        # Returns task id with given homework name and task number

        con, cur = self.__create_connection_and_cursor()

        cur.execute("SELECT task_id FROM tasks WHERE homework_name = ? AND task_number = ?",
                    (homework_name, task_number))
        task_id = cur.fetchone()

        # Returns None if there is no such task
        if task_id is None:
            return None

        return task_id[0]

    def get_right_answer_for_the_task(self, homework_name: str, task_number: int):
        # Returns right answer for the task with given homework name and task number

        con, cur = self.__create_connection_and_cursor()

        cur.execute("SELECT right_answer FROM tasks WHERE homework_name = ? AND task_number = ?",
                    (homework_name, task_number))
        right_answer = cur.fetchone()

        # If there is no such task just returns None
        if right_answer is None:
            return None

        return right_answer[0]

    def get_user_answer_for_the_task(self, login: str, homework_name: str, task_number: int):
        # Returns the answer user gave for the given task

        user_id = self.get_user_id_by_login(login)

        # If there is no such user, we just return None
        if user_id is None:
            return None

        task_id = self.get_task_id(homework_name, task_number)

        # If there is no such task, we just return None
        if task_id is None:
            return None

        con, cur = self.__create_connection_and_cursor()

        cur.execute("SELECT user_answer FROM results WHERE user_id = ? AND task_id = ?", (user_id, task_id))
        answer = cur.fetchone()

        # If user didn't give answer to that task we return empty string
        if answer is None:
            return ''

        return answer[0]

    def send_answer_for_the_task(self, login: str, homework_name: str, task_number: int, answer: str):
        # Writes info about user answer for the particular task

        # If user has already given an answer to this task we should raise an exception
        current_answer = self.get_user_answer_for_the_task(login, homework_name, task_number)
        if current_answer is not None and current_answer != '':
            raise RuntimeError

        user_id = self.get_user_id_by_login(login)

        # If there is no such user, we just return None
        if user_id is None:
            return None

        task_id = self.get_task_id(homework_name, task_number)

        # If there is no such task, we just return None
        if task_id is None:
            return None

        con, cur = self.__create_connection_and_cursor()

        cur.execute("INSERT INTO results (user_id, task_id, user_answer) VALUES (?, ?, ?)", (user_id, task_id, answer))
        con.commit()

        return self.get_right_answer_for_the_task(homework_name, task_number)

    # TODO return homework not homework name
    def get_all_homeworks_names(self) -> list[str]:
        # Returns list of homeworks names

        con, cur = self.__create_connection_and_cursor()

        cur.execute("SELECT DISTINCT homework_name FROM tasks")

        # We need to take the first element in each list
        return [data[0] for data in cur.fetchall()]

    # TODO return homework not homework name
    def get_all_homeworks_names_for_grade(self, grade: int) -> list[str]:
        # Returns list of homeworks names for given grade

        con, cur = self.__create_connection_and_cursor()

        cur.execute("SELECT DISTINCT homework_name FROM tasks WHERE grade = ?", (grade,))

        # We need to take the first element in each list
        return [data[0] for data in cur.fetchall()]

    def get_homework_by_name(self, homework_name: str):
        # Returns the object of class Homework corresponding to the given homework name

        con, cur = self.__create_connection_and_cursor()

        cur.execute("SELECT right_answer, grade FROM tasks WHERE homework_name = ?", (homework_name,))
        info = cur.fetchall()

        # If there is no such tasks with given homework name we return None
        if len(info) == 0:
            return None

        grade = info[0][1]
        right_answers = [data[0] for data in info]

        return Homework(homework_name, grade, right_answers)

    def get_list_of_unsolved_tasks(self, login: str, homework_name: str):
        # Returns a list of tasks in particular homework on which user didn't give any answer

        homework = self.get_homework_by_name(homework_name)

        # if there is no such homework we return None
        if homework is None:
            return None

        user = self.get_user_by_login(login)

        # if there is no such user we return None
        if user is None:
            return None

        # For each task we check if there is an answer
        unsolved_tasks = []
        for i in range(len(homework.right_answers)):
            if self.get_user_answer_for_the_task(login, homework_name, i + 1) == '':
                unsolved_tasks.append(i + 1)

        return unsolved_tasks

    def get_all_users_with_status(self, status) -> list[User]:
        # Returns list of all the users with given status in the database

        con, cur = self.__create_connection_and_cursor()

        # Get list of logins with given status
        cur.execute("SELECT login FROM users WHERE status = ?", (status,))

        # We need only the first element in the tuple
        logins = [data[0] for data in cur.fetchall()]

        # Getting users from logins
        users = [self.get_user_by_login(login) for login in logins]

        return users

    def get_results(self, status, homework_name: str):
        """
        Returns list of the next pairs:
        First element - User object
        Second element - list of the pairs: (user_answer, right_answer)
        Second element has the length of the amount of tasks in the homework with the given name
        """

        users = self.get_all_users_with_status(status)
        homework = self.get_homework_by_name(homework_name)

        # If there is no such homework just return None
        if homework is None:
            return None

        results: list[tuple[User, list[tuple[str, str]]]] = []
        for user in users:
            # We need only user with the same grade as in the homework
            if user.grade != homework.grade:
                continue

            # Going through all the tasks and collecting info about given answers
            answers: list[tuple[str, str]] = []
            for i in range(len(homework.right_answers)):
                user_answer = self.get_user_answer_for_the_task(user.login, homework_name, i + 1)
                right_answer = homework.right_answers[i]
                answers.append((user_answer, right_answer))
            results.append((user, answers))

        return results
