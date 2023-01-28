import sqlite3
from typing import Optional
from json import dumps, loads
import os

from bot.entities.result import Result
from bot.entities.task import Task
from bot.entities.user import User
from bot.entities.homework import Homework
from bot.constants import SUPER_ADMIN_STATUS, SUPER_ADMIN_LOGIN, SUPER_ADMIN_PASSWORD, UNAUTHORIZED_TELEGRAM_ID, \
    ADMINS, ADMIN_STATUS, PATH_TO_SOLUTION_FILES, PATH_TO_STATEMENTS_FILES


class DatabaseHelper:
    def __init__(self, path_to_database: str, database_name: str):
        self.database_path: str = path_to_database + database_name
        self.create_database()

    def __create_connection_and_cursor(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        # Returns connection and cursor to our database
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        # Activating ability to use foreign keys
        cur.execute("PRAGMA foreign_keys = ON")
        con.commit()

        return con, cur

    def create_database(self) -> None:
        con, cur = self.__create_connection_and_cursor()

        # Creates database with particular tables and relationships between them

        # Creating table with info about the users
        cur.execute("CREATE TABLE IF NOT EXISTS users("
                    "user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "login TEXT NOT NULL UNIQUE,"
                    "password TEXT NOT NULL,"
                    "status TEXT NOT NULL,"
                    "telegram_id INTEGER NOT NULL,"
                    "amount_of_mana INTEGER NOT NULL,"
                    "grade INTEGER);")

        # Creating table with info about the homeworks
        cur.execute("CREATE TABLE IF NOT EXISTS homeworks("
                    "homework_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "homework_name TEXT NOT NULL UNIQUE,"
                    "is_quest INTEGER NOT NULL,"
                    "grade INTEGER NOT NULL)")

        # Creating table with info about the tasks
        cur.execute("CREATE TABLE IF NOT EXISTS tasks("
                    "task_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "task_number TEXT NOT NULL,"
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
                    "text_clarification TEXT NOT NULL,"
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

    def add_user(self, user: User) -> None:
        # Creating new user with the given parameters

        # If we already have user with given login there should be an exception
        if self.get_user_by_login(user.login) is not None:
            raise RuntimeError

        con, cur = self.__create_connection_and_cursor()

        cur.execute("INSERT INTO users (login, password, status, telegram_id, grade, amount_of_mana) "
                    "VALUES (?, ?, ?, ?, ?, ?)", (user.login, user.password, user.status,
                                                  user.telegram_id, user.grade, user.amount_of_mana))
        con.commit()

    def get_user_by_login(self, login: str) -> Optional[User]:
        con, cur = self.__create_connection_and_cursor()

        # Getting user with the given login

        cur.execute("SELECT login, password, status, telegram_id, amount_of_mana, grade, user_id "
                    "FROM users "
                    "WHERE login = ?", (login,))

        user_parameters = cur.fetchone()

        # If there is no such user just return None
        if user_parameters is None:
            return None

        # Returning user with the given parameters
        return User(*user_parameters)

    def get_user_by_user_id(self, user_id: int) -> Optional[User]:
        con, cur = self.__create_connection_and_cursor()

        # Getting user with the corresponding user id

        cur.execute("SELECT login, password, status, telegram_id, amount_of_mana, grade, user_id "
                    "FROM users "
                    "WHERE user_id = ?", (user_id,))

        user_data = cur.fetchone()

        # If there is no such user just return None
        if user_data is None:
            return None

        # Returning user login with the given parameters
        return User(*user_data)

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        con, cur = self.__create_connection_and_cursor()

        # Getting user with the given telegram_id

        cur.execute("SELECT login, password, status, telegram_id, amount_of_mana, grade, user_id "
                    "FROM users "
                    "WHERE telegram_id = ?", (telegram_id,))

        user_parameters = cur.fetchone()

        # If there is no such user just return None
        if user_parameters is None:
            return None

        # Returning user with the given parameters
        return User(*user_parameters)

    def change_user_status(self, login: str, new_status: str) -> None:
        con, cur = self.__create_connection_and_cursor()

        cur.execute("UPDATE users SET status = ? WHERE login = ?", (new_status, login))
        con.commit()

    def change_user_mana_amount(self, login: str, new_mana_amount: int) -> None:
        con, cur = self.__create_connection_and_cursor()

        cur.execute("UPDATE users SET amount_of_mana = ? WHERE login = ?", (new_mana_amount, login))
        con.commit()

    def change_user_telegram_id(self, login: str, new_telegram_id: int) -> None:
        con, cur = self.__create_connection_and_cursor()

        cur.execute("UPDATE users SET telegram_id = ? WHERE login = ?", (new_telegram_id, login))
        con.commit()

    def delete_user_by_login(self, login: str) -> None:
        con, cur = self.__create_connection_and_cursor()

        # Getting user with such login
        user = self.get_user_by_login(login)

        # If there is no such user just do nothing
        if user is None:
            return None

        # Deleting all user's solutions
        solutions_data = cur.execute("SELECT file_answer, task_id FROM results WHERE user_id = ?", (user.user_id,))
        for solution_extension, task_id in solutions_data:
            self.delete_file(self.__get_solution_filename(user.user_id, task_id, solution_extension))

        cur.execute("DELETE FROM users WHERE login = ?", (login,))
        con.commit()

    def get_all_users_with_status(self, status: str) -> list[User]:
        # Returns list of all the users with given status in the database

        con, cur = self.__create_connection_and_cursor()

        # Get list of logins with given status
        cur.execute("SELECT login FROM users WHERE status = ?", (status,))

        # We need only the first element in the tuple
        logins = [data[0] for data in cur.fetchall()]

        # Getting users from logins
        users = [self.get_user_by_login(login) for login in logins]

        return users

    def get_user_answer_for_the_task(self, login: str, homework_name: str, task_number: int) -> Optional[Result]:
        # Returns the answer user gave for the given task

        user = self.get_user_by_login(login)

        # If there is no such user, we just return None
        if user is None:
            return None

        task = self.get_task(homework_name, task_number)

        # If there is no such task, we just return None
        if task is None:
            return None

        con, cur = self.__create_connection_and_cursor()

        # We get answer of the user
        cur.execute("SELECT user_id, task_id, text_answer, text_clarification, file_answer"
                    " FROM results WHERE user_id = ? AND task_id = ?",
                    (user.user_id, task.task_id))
        result_params = cur.fetchone()

        # If user didn't give answer to that task we return empty string
        if result_params is None:
            return None

        filename = self.__get_solution_filename(user.user_id, task.task_id, result_params[4])
        return Result(result_params[0], result_params[1], result_params[2], result_params[3],
                      (self.get_file_data(filename), result_params[4]))

    def get_task(self, homework_name: str, task_number: int) -> Optional[Task]:
        # Returns task id with given homework name and task number

        homework = self.get_homework_by_name(homework_name)
        # If there is no such homework return None
        if homework is None:
            return None

        # If there is no such task return None
        if task_number > len(homework.tasks):
            return None

        return homework.tasks[task_number - 1]

    def send_answer_for_the_task(self, login: str, homework_name: str, task_number: int,
                                 text_answer: str, text_clarification: str,
                                 file_answer: tuple[bytes, str]) -> Optional[list[str]]:
        # Writes info about user answer for the particular task

        # If user has already given an answer to this task we should raise an exception
        current_answer = self.get_user_answer_for_the_task(login, homework_name, task_number)
        if current_answer is not None:
            raise RuntimeError("User has already given an answer for that task")

        user = self.get_user_by_login(login)

        # If there is no such user, we just return None
        if user is None:
            return None

        task = self.get_task(homework_name, task_number)

        # If there is no such task, we just return None
        if task is None:
            return None

        con, cur = self.__create_connection_and_cursor()

        # Saving our solution file to special directory
        # Even if there is no solution file we will create an empty file
        filename = self.__get_solution_filename(user.user_id, task.task_id, file_answer[1])
        self.save_file_data(filename, file_answer[0])

        # Writing info about the answer
        cur.execute("INSERT INTO results (user_id, task_id, text_answer, text_clarification, file_answer) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (user.user_id, task.task_id, text_answer, text_clarification, file_answer[1]))
        con.commit()

        return self.get_right_answers_for_the_task(homework_name, task_number)

    def change_user_answer_for_the_task(self, login: str, homework_name: str, task_number: int,
                                        new_text_answer: str) -> None:
        # Changes user answer for the given task

        user = self.get_user_by_login(login)
        if user is None:
            return None

        task = self.get_task(homework_name, task_number)
        if task is None:
            return None

        con, cur = self.__create_connection_and_cursor()

        cur.execute("UPDATE results SET text_answer = ? WHERE user_id = ? AND task_id = ?",
                    (new_text_answer, user.user_id, task.task_id))
        con.commit()

    def add_homework(self, homework: Homework) -> None:
        # Creating new homework with the given parameters

        # If there is already a homework with given name we should raise an exception
        if self.get_homework_by_name(homework.name) is not None:
            raise RuntimeError("There is already a homework with the given name")

        self.__add_homework_without_checking(homework)

        # We need to refresh our homework_id
        homework.homework_id = self.get_homework_by_name(homework.name).homework_id

        for i in range(len(homework.tasks)):
            task = homework.tasks[i]
            self.__add_task(task, homework)

    def __add_homework_without_checking(self, homework: Homework) -> None:
        con, cur = self.__create_connection_and_cursor()

        cur.execute("INSERT INTO homeworks (homework_name, grade, is_quest) VALUES (?, ?, ?)",
                    (homework.name, homework.grade, homework.is_quest))

        con.commit()

    def __add_task_without_checking(self, task: Task, homework: Homework) -> None:
        con, cur = self.__create_connection_and_cursor()

        cur.execute("INSERT INTO tasks (task_number, right_answers, text_statement, file_statement, homework_id) "
                    "VALUES (?, ?, ?, ?, ?)", (task.task_number, dumps(task.right_answers), task.text_statement,
                                               task.file_statement[1], homework.homework_id))

        con.commit()

    def __add_task(self, task: Task, homework: Homework) -> None:
        if self.get_task(homework.name, task.task_number) is not None:
            return None

        self.__add_task_without_checking(task, homework)

        # We need to refresh our task_id
        task.task_id = self.get_task(homework.name, task.task_number).task_id

        # Saving task statement file in the special directory
        self.save_file_data(self.__get_task_filename(homework.homework_id, task.task_id,
                                                     task.file_statement[1]), task.file_statement[0])

    def delete_homework_by_name(self, homework_name: str) -> None:
        con, cur = self.__create_connection_and_cursor()

        homework = self.get_homework_by_name(homework_name)
        if homework is None:
            return None

        # Deleting all files with statements for this homework
        for task in homework.tasks:
            self.delete_file(self.__get_task_filename(homework.homework_id, task.task_id, task.file_statement[1]))

        cur.execute("DELETE FROM homeworks WHERE homework_name = ?", (homework_name,))
        con.commit()

    def get_right_answers_for_the_task(self, homework_name: str, task_number: int) -> Optional[list[str]]:
        # Returns right answers for the task with given homework name and task number

        homework = self.get_homework_by_name(homework_name)

        # If there is no such homework return None
        if homework is None:
            return None

        # If there is no such task number return None
        if task_number > len(homework.tasks):
            return None

        return homework.tasks[task_number - 1].right_answers

    def get_all_homeworks(self, is_quest: int = 0) -> list[Homework]:
        # Returns list of homeworks

        con, cur = self.__create_connection_and_cursor()

        cur.execute("SELECT homework_name FROM homeworks WHERE is_quest = ?", (is_quest,))

        # We need only the first element in the tuples
        homeworks_names = [item[0] for item in cur.fetchall()]

        return [self.get_homework_by_name(homework_name) for homework_name in homeworks_names]

    def get_all_homeworks_for_grade(self, grade: int, is_quest: int = 0) -> list[Homework]:
        # Returns list of homeworks names for given grade

        return [homework for homework in self.get_all_homeworks(is_quest) if homework.grade == grade]

    def get_homework_by_name(self, homework_name: str) -> Optional[Homework]:
        # Returns the object of class Homework corresponding to the given homework name

        con, cur = self.__create_connection_and_cursor()

        cur.execute("SELECT homework_id, homework_name, grade, is_quest FROM homeworks "
                    "WHERE homework_name = ?", (homework_name,))
        raw_homework = cur.fetchone()

        # If there is no such homework with given name we return None
        if raw_homework is None:
            return None

        homework = Homework(raw_homework[1], raw_homework[2], [], raw_homework[0], raw_homework[3])

        # Finding all the tasks for our homework
        cur.execute("SELECT task_id, task_number, right_answers, text_statement, file_statement, homework_id "
                    "FROM tasks WHERE homework_id = ?", (homework.homework_id,))

        raw_tasks = cur.fetchall()

        homework.tasks = [Task(raw_task[1], loads(raw_task[2]), raw_task[3],
                               (self.get_file_data(self.__get_task_filename(raw_task[5], raw_task[0], raw_task[4])),
                                raw_task[4]), raw_task[0], raw_task[5]) for raw_task in raw_tasks]

        return homework

    def get_list_of_unsolved_tasks(self, login: str, homework_name: str) -> Optional[list[int]]:
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
        for i in range(len(homework.tasks)):
            if self.get_user_answer_for_the_task(login, homework_name, i + 1) is None:
                unsolved_tasks.append(i + 1)

        return unsolved_tasks

    def get_results(self, status: str, homework_name: str) -> Optional[list[tuple[User, list[Optional[bool]]]]]:
        """
        Returns list of the next pairs:
        First element - User object
        Second element - list of the values: (True - correct answer, False - wrong answer, None - no answer)
        Second element has the length of the amount of tasks in the homework with the given name
        """

        users = self.get_all_users_with_status(status)
        homework = self.get_homework_by_name(homework_name)

        # If there is no such homework just return None
        if homework is None:
            return None

        results: list[tuple[User, list[Optional[bool]]]] = []
        for user in users:
            # We need only user with the same grade as in the homework
            if user.grade != homework.grade:
                continue

            # Going through all the tasks and collecting info about given answers
            answers: list[Optional[bool]] = []
            for i in range(len(homework.tasks)):
                user_answer = self.get_user_answer_for_the_task(user.login, homework_name, i + 1)
                right_answers = homework.tasks[i].right_answers

                # Checking if user answer is correct
                if user_answer is None:
                    answers.append(None)
                elif user_answer.text_answer in right_answers:
                    answers.append(True)
                else:
                    answers.append(False)

            results.append((user, answers))

        return results

    @staticmethod
    def get_file_data(filename: str) -> Optional[bytes]:
        # Gets data in bytes from the file called "filename"
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = f.read()
            return data
        return None

    @staticmethod
    def save_file_data(filename: str, data: bytes) -> None:
        # Writes data in bytes to the file called "filename"
        with open(filename, 'wb') as f:
            if data is None:
                return
            f.write(data)

    @staticmethod
    def delete_file(filename: str) -> None:
        try:
            os.remove(filename)
        except OSError as error:
            pass

    @staticmethod
    def get_extension(filename: str) -> str:
        ext = os.path.splitext(filename)[1]
        if ext.startswith('.'):  # We don't want to have dot in the beginning of the extension
            ext = ext[1:]
        return ext

    @staticmethod
    def __get_task_filename(homework_id: int, task_id: int, extension: str) -> str:
        filename = f"{PATH_TO_STATEMENTS_FILES}/{str(homework_id)}_{str(task_id)}.{extension}"
        return filename

    @staticmethod
    def __get_solution_filename(user_id: int, task_id: int, extension: str) -> str:
        filename = f"{PATH_TO_SOLUTION_FILES}/{str(user_id)}_{str(task_id)}.{extension}"
        return filename
