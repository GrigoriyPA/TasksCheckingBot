class Result:
    def __init__(self, user_id: int, task_id: int, text_answer: str, photo_answer: bytes):
        self.user_id: int = user_id
        self.task_id: int = task_id
        self.text_answer: str = text_answer
        self.photo_answer: bytes = photo_answer

    def __str__(self):
        return f"Result: self.user_id = {self.user_id}, self.task_id = {self.task_id}"
