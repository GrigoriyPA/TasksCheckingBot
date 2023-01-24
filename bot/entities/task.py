class Task:
    def __init__(self, homework_id: int, task_number: int, right_answers: list[str], text_statement: str,
                 file_statement: tuple[bytes, str], task_id: int = 0):
        self.homework_id: int = homework_id
        self.task_number: int = task_number
        self.right_answers: list[str] = right_answers
        self.text_statement: str = text_statement
        self.file_statement: tuple[bytes, str] = file_statement
        self.task_id: int = task_id

    def __str__(self):
        return f"Task: homework_id = {self.homework_id}, index_in_homework = {self.task_number}"
