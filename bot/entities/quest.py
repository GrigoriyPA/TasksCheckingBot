from bot.entities.task import Task


class Quest:
    def __init__(self, name: str, grade: int, task: Task):
        self.name: str = name
        self.grade: int = grade
        self.task: Task = task

    def __str__(self):
        return f"Quest: name = {self.name}, grade = {self.grade}"
