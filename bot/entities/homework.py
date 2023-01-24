from bot.entities.task import Task


class Homework:
    def __init__(self, name: str, grade: int, tasks: list[Task]):
        self.name: str = name
        self.grade: int = grade
        self.tasks: list[Task] = tasks

    def __str__(self):
        return f"Homework: name = {self.name}, grade = {self.grade}"
