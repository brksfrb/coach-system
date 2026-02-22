from .user import User
from dataclasses import dataclass, asdict
from ..Extras.date import CustomDate
from logger import logger

@dataclass
class Homework:
    title: str
    description: str
    start_date: CustomDate
    end_date: CustomDate
    subject: str
    objective: str
    num_questions: int
    condition: str

    @property
    def jsonized(self):
        data = asdict(self)
        # Convert CustomDate fields to strings
        for field in ['start_date', 'end_date']:
            data[field] = str(getattr(self, field))
        return data

class Student(User):
    def __init__(self, username: str, password: str, name: str, surname: str, gender: str, grade: int, teacher):
        super().__init__(username, password, name, surname, "student", gender)
        self._grade = grade
        self._teacher = teacher
        self._parents: list = []
        self._homeworks: list[Homework] = []
        self._notes: str = ""

    def __setstate__(self, state):
        self.__dict__.update(state)

        if "_homeworks" not in state:
            self._homeworks = []
        if "_notes" not in state:
            self._notes = ""

    def add_parent(self, new_parent):
        self._parents.append(new_parent)

    def add_homework(self, title: str, description: str, start_date: CustomDate, end_date: CustomDate, subject: str, objective: str, num_questions: int):
        new_homework = Homework(title, description, start_date, end_date, subject, objective, num_questions, "na")
        self._homeworks.append(new_homework)

    @property
    def grade(self):
        return self._grade
    @property
    def teacher(self):
        return self._teacher
    @property
    def homeworks(self):
        return self._homeworks[::-1]
    @property
    def notes(self):
        return self._notes
    @notes.setter
    def notes(self, value):
        if not isinstance(value, str):
            logger.error("Only str can be used as note")
            return
        self._notes = value
    @property
    def lessons(self):
        return self._teacher.program.get_lessons_by_username(self._username)

    @property
    def total_homeworks(self):
        return len(self._homeworks)
    @property
    def done_homeworks(self):
        return len([h for h in self._homeworks if h.condition == "done"])
    @property
    def missing_homeworks(self):
        return len([h for h in self._homeworks if h.condition == "missing"])