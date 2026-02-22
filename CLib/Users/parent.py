from .user import User
from .student import Student
from enum import Enum
from dataclasses import dataclass

class Relation(Enum):
    # (key, english, turkish)
    MOTHER = ("mother", "Mother", "Annesi")
    FATHER = ("father", "Father", "Babası")
    def __init__(self, code, en, tr):
        self.code = code
        self.en = en
        self.tr = tr

@dataclass
class ParentInformation:
    name: str
    surname: str
    gender: str
    relation: Relation

class Parent(User):
    def __init__(self, username: str, password: str, name: str, surname: str, gender: str, student: Student, relation: Relation):
        super().__init__(username, password, name, surname, "parent", gender)
        self._student: Student = student
        self._relation: Relation = relation

    @property
    def student(self):
        return self._student
    @property
    def relation(self):
        return self._relation