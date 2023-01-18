class User:
    def __init__(self, login: str, password: str, status: str, telegram_id: int, grade: int = -1, user_id: int = -1):
        self.login: str = login
        self.password: str = password
        self.status: str = status
        self.telegram_id: int = telegram_id
        self.grade: int = grade
        self.user_id: int = user_id

    def __str__(self):
        return f"Student: login = {self.login}, password = {self.password}, " \
               f"status = {self.status}, telegram_id = {self.telegram_id}, grade = {self.grade}"
