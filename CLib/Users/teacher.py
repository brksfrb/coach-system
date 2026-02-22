from .user import User
from .student import Student
from ..Extras.configs import TeacherConfig, Hour
from ..Extras.date import days_of_week_en, en_to_tr_day
from dataclasses import dataclass
from logger import logger

@dataclass
class ProgramBox:
    student: Student | None

class Program:
    def __init__(self, num_columns: int):
        self.num_columns = num_columns
        self._boxes = {day: {i: ProgramBox(None) for i in range(num_columns)} for day in days_of_week_en}
        self._hours = {i: (Hour(f"{i + 10}", "00"), Hour(f"{i + 10}", "30")) for i in range(num_columns)}

    def get_box(self, day, index):
        try:
            return self._boxes[day][index]
        except KeyError:
            return None
    def set_box(self, day, index, new_student: Student):
        self._boxes[day][index] = ProgramBox(new_student)

    def get_lessons_by_username(self, username: str):
        ret = []
        for day, boxes in self._boxes.items():
            for index, box in boxes.items():
                if box and box.student and box.student.username == username:
                    ret.append((en_to_tr_day(day), self._hours[index]))
        return ret

    def change_hours(self, column_index: int, new_hours: tuple[Hour, Hour]):
        if column_index > self.num_columns:
            logger.error("Column index out of num_columns.")
            return False
        self._hours[column_index] = new_hours
        return True

    @property
    def hours(self):
        return self._hours

    def rearrange_boxes(self, num_columns: int):
        """Resize number of columns per day while keeping existing student data."""
        self.num_columns = num_columns
        for day, program_day in self._boxes.items():
            old_students = program_day.students.copy()
            new_students = {}

            for i in range(1, num_columns + 1):
                new_students[i] = old_students.get(i, None)  # preserve old data if possible

            program_day.students = new_students

class Teacher(User):
    def __init__(self, username: str, password: str, name: str, surname: str, gender: str, config: TeacherConfig):
        super().__init__(username, password, name, surname, "teacher", gender)
        self._students: list[Student] = []
        self._config = config
        self._program: Program = Program(5)

    def __setstate__(self, state):
        self.__dict__.update(state)

        if "_program" not in state:
            self._program = Program(5)

    def create_student(self, new_student: Student):
        if self.check_student_availability():
            self._students.append(new_student)

    def remove_student(self, old_student: Student):
        if old_student in self._students:
            self._students.remove(old_student)
            logger.info("Successfully removed student.")
        else:
            logger.error("Couldn't remove the student (Does not exist)")

    def check_student_availability(self):
        return len(self.students) < self.config.MAX_STUDENTS

    @property
    def students(self):
        return self._students

    @property
    def config(self):
        return self._config
    @property
    def program(self):
        return self._program