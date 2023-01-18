class Homework:
    def __init__(self, name: str, grade: int, right_answers: list[str]):
        self.name: str = name
        self.grade: int = grade
        self.right_answers: list[str] = right_answers

    def __str__(self):
        return f"Homework: name = {self.name}, grade = {self.grade}, right_answers = {'; '.join(self.right_answers)}"
