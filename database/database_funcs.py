import sqlite3
from user import User
from homework import Homework


class DatabaseHelper:
    def __init__(self, path_to_database: str, database_name: str):
        self.database_path: str = path_to_database + database_name

    def create_database(self):
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        # USE ONLY WHEN CREATING NEW DATABASE

        # Creates database with particular tables and relationships between them
        # Returns connection to that database

        # Activating ability to use foreign keys
        cur.execute("PRAGMA foreign_keys = ON")

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
                    "right_answer TEXT NOT NULL);")

        # Creating table with results of solving tasks by users
        cur.execute("DROP TABLE IF EXISTS results")
        cur.execute("CREATE TABLE results("
                    "user_id INTEGER NOT NULL,"
                    "task_id INTEGER NOT NULL,"
                    "user_answer TEXT NOT NULL,"
                    "FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,"
                    "FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE SET NULL,"
                    "PRIMARY KEY (user_id, task_id));")

        # Saving changes
        con.commit()

    def add_user(self, user: User):
        # Creating new user with the given parameters
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        cur.execute("INSERT INTO users (login, password, status, telegram_id) "
                    "VALUES (?, ?, ?, ?)", (user.login, user.password, user.status, user.telegram_id))
        con.commit()

    def get_user_by_login(self, login: str):
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

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

    def get_user_by_telegram_id(self, telegram_id: int):
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

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
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        cur.execute("UPDATE users SET status = ? WHERE login = ?", (new_status, login))
        con.commit()

    def change_user_telegram_id(self, login: str, new_telegram_id: int):
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        cur.execute("UPDATE users SET telegram_id = ? WHERE login = ?", (new_telegram_id, login))
        con.commit()

    def delete_user_by_login(self, login: str):
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        cur.execute("DELETE FROM users WHERE login = ?", (login,))
        con.commit()

    def add_homework(self, homework: Homework):
        # Creating new homework with the given parameters
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        # There is a line in the database for each task in the homework
        for i in range(len(homework.right_answers)):
            right_answer = homework.right_answers[i]
            cur.execute("INSERT INTO tasks (homework_name, task_number, right_answer) "
                        "VALUES (?, ?, ?)", (homework.name, i + 1, right_answer))

        con.commit()

    def delete_homework_by_name(self, homework_name: str):
        # Deletes all the tasks in the homework by it's name
        con = sqlite3.connect(self.database_path)
        cur = con.cursor()

        cur.execute("DELETE FROM tasks WHERE homework_name = ?", (homework_name,))
        con.commit()
