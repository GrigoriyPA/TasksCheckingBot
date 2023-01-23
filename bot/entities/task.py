class Task:
    def __init__(self, homework_id: int, index_in_homework: int, right_answers: list[str], text_statement: str,
                 photo_statement: bytes):
        self.homework_id: int = homework_id
        self.index_in_homework: int = index_in_homework
        self.right_answers: list[str] = right_answers
        self.text_statement: str = text_statement
        self.photo_statement: bytes = photo_statement

    def __str__(self):
        return f"Task: homework_id = {self.homework_id}, index_in_homework = {self.index_in_homework}"
