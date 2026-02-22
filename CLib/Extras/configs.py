from dataclasses import dataclass
from enum import Enum

@dataclass
class Module:
    name: str
    pretty_name: str

@dataclass
class Subject:
    key: str
    name: str

@dataclass
class Hour:
    """
    Hour class to store program hours

    Attributes:
        hour (int): Hour in 24H format
        minute (int): Minute in 24H format
    """
    hour: str
    minute: str

    def __repr__(self):
        return f"{self.hour}:{self.minute}"

@dataclass
class Row:
    """
    Row class to store program rows

    Attributes:
        start_hour (Hour): Hour as Hour object
        end_hour (Hour): Hour as Hour object
    """
    start_hour: Hour
    end_hour: Hour

@dataclass
class TeacherConfig:
    MAX_STUDENTS: int
    MODULES: list[str]

@dataclass
class Objective:
    """
    Objective class to store objectives for homeworks

    Attributes:
        subject (str): The subject name (e.g., "math", "physics").
        objective (str): The objective text or description.
        code (int): The objective's unique numeric code.
        depth (int): The hierarchical depth or level of detail.
    """
    subject: str
    objective: str
    code: int
    depth: int

@dataclass
class Objectives:
    objectives: list[Objective]

@dataclass
class CreationManagerConfig:
    """
    CreationManager Config class to store config

    Attributes:
        DATABASE_PATH (str): The path to the database
        MAX_USERS (int): Max number of users
        MAX_TEACHERS (int): Max number of teachers
        MAX_STUDENTS (int): Max number of students
        AVAILABLE_MODULES (list[Module]): Available modules for teachers
        AVAILABLE_SUBJECTS (list[Subject]): Available subjects
        HIGH_SCHOOL_OBJECTIVES (Objectives): Objectives for homework assignment etc.
    """
    DATABASE_PATH: str
    MAX_USERS: int
    MAX_TEACHERS: int
    MAX_STUDENTS: int
    AVAILABLE_MODULES: list[Module]
    AVAILABLE_SUBJECTS: list[Subject]
    HIGH_SCHOOL_OBJECTIVES: Objectives