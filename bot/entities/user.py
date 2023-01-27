class User:
    def __init__(self, login: str, password: str, status: str, telegram_id: int, amount_of_mana: int = 0,
                 grade: int = 0, user_id: int = 0):
        self.login: str = login
        self.password: str = password
        self.status: str = status
        self.telegram_id: int = telegram_id
        self.amount_of_mana: int = amount_of_mana
        self.grade: int = grade
        self.user_id: int = user_id

    def __str__(self):
        return f"Student: login = {self.login}, password = {self.password}, " \
               f"status = {self.status}, telegram_id = {self.telegram_id}, grade = {self.grade}"
