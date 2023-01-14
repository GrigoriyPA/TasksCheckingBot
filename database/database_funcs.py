import sqlite3
from user import User


class DatabaseHelper:
    def __init__(self, path_to_database, database_name):
        self.DATABASE_NAME = database_name
        self.con = sqlite3.connect(path_to_database + database_name)
        self.cur = self.con.cursor()

    def __del__(self):
        self.con.close()

    def create_database(self):
        # USE ONLY WHEN CREATING NEW DATABASE

        # Creates database with particular tables and relationships between them
        # Returns connection to that database

        # Activating ability to use foreign keys
        self.cur.execute("PRAGMA foreign_keys = ON")

        # Creating table with info about the users
        self.cur.execute("DROP TABLE users")
        self.cur.execute("CREATE TABLE users("
                         "user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                         "login TEXT NOT NULL UNIQUE,"
                         "password TEXT NOT NULL,"
                         "status TEXT NOT NULL,"
                         "telegram_id INTEGER NOT NULL UNIQUE);")

        # Creating table with info about the tasks
        self.cur.execute("DROP TABLE tasks")
        self.cur.execute("CREATE TABLE tasks("
                         "task_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                         "homework_number INTEGER NOT NULL,"
                         "task_number INTEGER NOT NULL,"
                         "right_answer TEXT NOT NULL);")

        # Creating table with results of solving tasks by users
        self.cur.execute("DROP TABLE results")
        self.cur.execute("CREATE TABLE results("
                         "user_id INTEGER NOT NULL,"
                         "task_id INTEGER NOT NULL,"
                         "user_answer TEXT NOT NULL,"
                         "FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,"
                         "FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE SET NULL,"
                         "PRIMARY KEY (user_id, task_id));")

        # Saving changes
        self.con.commit()

    def create_user(self, user: User):
        # Creating new user with the given parameters
        self.cur.execute("INSERT INTO users (login, password, status, telegram_id) "
                         "VALUES (?, ?, ?, ?)", (user.login, user.password, user.status, user.telegram_id))
        self.con.commit()

    def get_user_by_login(self, login):
        # Getting user with the given login

        self.cur.execute("SELECT login, password, status, telegram_id "
                                "FROM users "
                                "WHERE login = ?", (login, ))

        user_parameters = self.cur.fetchone()

        # If there is no such user just return None
        if user_parameters is None:
            return None

        # Returning user with the given parameters
        return User(*user_parameters)

    def get_user_by_telegram_id(self, telegram_id):
        # Getting user with the given telegram_id

        self.cur.execute("SELECT login, password, status, telegram_id "
                                "FROM users "
                                "WHERE telegram_id = ?", (telegram_id, ))

        user_parameters = self.cur.fetchone()

        # If there is no such user just return None
        if user_parameters is None:
            return None

        # Returning user with the given parameters
        return User(*user_parameters)

    def change_user_status(self, login, new_status):
        self.cur.execute("UPDATE users SET status = ? WHERE login = ?", (new_status, login))
        self.con.commit()

    def change_user_telegram_id(self, login, new_telegram_id):
        self.cur.execute("UPDATE users SET telegram_id = ? WHERE login = ?", (new_telegram_id, login))
        self.con.commit()


# dh = DatabaseHelper('database.db')
# dh.create_database()
# a = User('a', 'b', 'c', 5)
# b = User('b', 'b', 'c', 6)
# c = User('c', 'b', 'c', 7)
# d = User('d', 'b', 'c', 8)
# dh.create_user(a)
# dh.create_user(b)
# dh.create_user(c)
# dh.create_user(d)
# dh.get_user_by_login('d')
# dh.change_user_status('ahg', 'bobobo')

