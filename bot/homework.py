class Homework:
    def __init__(self, name: str, right_answers: list[str]):
        self.name: str = name
        self.right_answers: list[str] = right_answers

    def __str__(self):
        return f"Homework: name = {self.name}, right_answers = {'; '.join(self.right_answers)}"
