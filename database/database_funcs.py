import sqlite3
from user import User
from homework import Homework


class DatabaseHelper:
    def __init__(self, path_to_database: str, database_name: str):
        self.database_path: str = path_to_database + database_name

    def create_connection_and_cursor(self):
        # Returns connection and cursor to our database
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        # Activating ability to use foreign keys
        cur.execute("PRAGMA foreign_keys = ON")
        con.commit()

        return con, cur

    def create_database(self):
        con, cur = self.create_connection_and_cursor()

        # USE ONLY WHEN CREATING NEW DATABASE

        # Creates database with particular tables and relationships between them

        # Creating table with info about the users
        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute("CREATE TABLE users("
                    "user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "login TEXT NOT NULL UNIQUE,"
                    "password TEXT NOT NULL,"
                    "status TEXT NOT NULL,"
                    "telegram_id INTEGER NOT NULL);")

        # Creating table with info about the tasks
        cur.execute("DROP TABLE IF EXISTS tasks")
        cur.execute("CREATE TABLE tasks("
                    "task_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "homework_name TEXT NOT NULL,"
                    "task_number INTEGER NOT NULL,"
                    "right_answer TEXT NOT NULL,"
                    "UNIQUE(homework_name, task_number))")

        # Creating table with results of solving tasks by users
        cur.execute("DROP TABLE IF EXISTS results")
        cur.execute("CREATE TABLE results("
                    "user_id INTEGER NOT NULL,"
                    "task_id INTEGER NOT NULL,"
                    "user_answer TEXT NOT NULL,"
                    "FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,"
                    "FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,"
                    "PRIMARY KEY (user_id, task_id));")

        # Saving changes
        con.commit()

    def add_user(self, user: User):
        # Creating new user with the given parameters

        con, cur = self.create_connection_and_cursor()

        # TODO adding same logins

        cur.execute("INSERT INTO users (login, password, status, telegram_id) "
                    "VALUES (?, ?, ?, ?)", (user.login, user.password, user.status, user.telegram_id))
        con.commit()

    def get_user_by_login(self, login: str):
        con, cur = self.create_connection_and_cursor()

        # Getting user with the given login

        cur.execute("SELECT login, password, status, telegram_id "
                    "FROM users "
                    "WHERE login = ?", (login,))

        user_parameters = cur.fetchone()

        # If there is no such user just return None
        if user_parameters is None:
            return None

        # Returning user with the given parameters
        return User(*user_parameters)

    def get_user_id_by_login(self, login: str):
        con, cur = self.create_connection_and_cursor()

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

    def get_user_by_telegram_id(self, telegram_id: int):
        con, cur = self.create_connection_and_cursor()

        # Getting user with the given telegram_id

        cur.execute("SELECT login, password, status, telegram_id "
                    "FROM users "
                    "WHERE telegram_id = ?", (telegram_id,))

        user_parameters = cur.fetchone()

        # If there is no such user just return None
        if user_parameters is None:
            return None

        # Returning user with the given parameters
        return User(*user_parameters)

    def change_user_status(self, login: str, new_status: str):
        con, cur = self.create_connection_and_cursor()

        cur.execute("UPDATE users SET status = ? WHERE login = ?", (new_status, login))
        con.commit()

    def change_user_telegram_id(self, login: str, new_telegram_id: int):
        con, cur = self.create_connection_and_cursor()

        cur.execute("UPDATE users SET telegram_id = ? WHERE login = ?", (new_telegram_id, login))
        con.commit()

    def delete_user_by_login(self, login: str):
        con, cur = self.create_connection_and_cursor()

        cur.execute("DELETE FROM users WHERE login = ?", (login,))
        con.commit()

    def add_homework(self, homework: Homework):
        # Creating new homework with the given parameters

        con, cur = self.create_connection_and_cursor()

        # There is a line in the database for each task in the homework
        for i in range(len(homework.right_answers)):
            right_answer = homework.right_answers[i]
            # TODO unique constraint
            cur.execute("INSERT INTO tasks (homework_name, task_number, right_answer) "
                        "VALUES (?, ?, ?)", (homework.name, i + 1, right_answer))

        con.commit()

    def delete_homework_by_name(self, homework_name: str):
        # Deletes all the tasks in the homework by it's name

        con, cur = self.create_connection_and_cursor()

        cur.execute("DELETE FROM tasks WHERE homework_name = ?", (homework_name,))
        con.commit()

    def get_task_id(self, homework_name: str, task_number: int):
        # Returns task id with given homework name and task number

        con, cur = self.create_connection_and_cursor()

        cur.execute("SELECT task_id FROM tasks WHERE homework_name = ? AND task_number = ?",
                    (homework_name, task_number))
        task_id = cur.fetchone()

        # Returns None if there is no such task
        if task_id is None:
            return None

        return task_id[0]

    def get_right_answer_for_the_task(self, homework_name: str, task_number: int):
        # Returns right answer for the task with given homework name and task number

        con, cur = self.create_connection_and_cursor()

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

        con, cur = self.create_connection_and_cursor()

        cur.execute("SELECT user_answer FROM results WHERE user_id = ? AND task_id = ?", (user_id, task_id))
        answer = cur.fetchone()

        # If user didn't give answer to that task we return empty string
        if answer is None:
            return ''

        return answer[0]

    def send_answer_for_the_task(self, login: str, homework_name: str, task_number: int, answer: str):
        # Writes info about user answer for the particular task

        user_id = self.get_user_id_by_login(login)

        # If there is no such user, we just return None
        if user_id is None:
            return None

        task_id = self.get_task_id(homework_name, task_number)

        # If there is no such task, we just return None
        if task_id is None:
            return None

        con, cur = self.create_connection_and_cursor()

        # TODO empty answer
        # TODO unique constraint

        cur.execute("INSERT INTO results (user_id, task_id, user_answer) VALUES (?, ?, ?)", (user_id, task_id, answer))
        con.commit()

        return self.get_right_answer_for_the_task(homework_name, task_number)

    def get_all_homeworks_names(self) -> list[str]:
        # Returns list of homeworks names

        con, cur = self.create_connection_and_cursor()

        cur.execute("SELECT DISTINCT homework_name FROM tasks")

        # We need to take the first element in each list
        return [data[0] for data in cur.fetchall()]

    def get_homework_by_name(self, homework_name: str):
        # Returns the object of class Homework corresponding to the given homework name

        con, cur = self.create_connection_and_cursor()

        cur.execute("SELECT right_answer FROM tasks WHERE homework_name = ?", (homework_name,))

        # We need to take the first element in each list
        right_answers = [data[0] for data in cur.fetchall()]

        # If there is no such tasks with given homework name we return None
        if len(right_answers) == 0:
            return None

        return Homework(homework_name, right_answers)

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
