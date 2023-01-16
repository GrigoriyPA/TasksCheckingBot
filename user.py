class User:
    def __init__(self, login: str, password: str, status: str, telegram_id: int, user_id: int = -1):
        self.login: str = login
        self.password: str = password
        self.status: str = status
        self.telegram_id: int = telegram_id
        self.user_id: int = user_id

    def __str__(self):
        return f"User: login = {self.login}, password = {self.password}, " \
               f"status = {self.status}, telegram_id = {self.telegram_id}"
