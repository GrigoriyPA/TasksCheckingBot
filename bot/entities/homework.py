from bot.entities.task import Task


class Homework:
    def __init__(self, name: str, grade: int, tasks: list[Task], homework_id_: int = 0, is_quest: int = 0):
        self.name: str = name
        self.grade: int = grade
        self.tasks: list[Task] = tasks
        self.homework_id: int = homework_id_
        self.is_quest: int = is_quest

    def __str__(self):
        return f"Homework: name = {self.name}, grade = {self.grade}"
