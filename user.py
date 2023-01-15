class User:
    def __init__(self, login: str, password: str, status: str, telegram_id: int):
        self.login: str = login
        self.password: str = password
        self.status: str = status
        self.telegram_id: int = telegram_id
