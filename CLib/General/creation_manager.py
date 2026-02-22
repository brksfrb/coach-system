import os, portalocker, pickle, shutil, time, secrets, string
from functools import wraps
from typing import Literal, Union
import re, unicodedata
from logger import logger

from ..Extras.configs import TeacherConfig, CreationManagerConfig
from ..Extras.date import CustomDate
from ..Extras.messaging import MessageData, Message
from ..Users.parent import Parent, ParentInformation
from ..Users.student import Student
from ..Users.system_admin import SystemAdmin
from ..Users.teacher import Teacher
from ..Users.user import User

class GlobalLimitReachedError(Exception):
    """Creation Manager global limit reached."""
    pass

class TeacherLimitReacherError(Exception):
    """Teacher limit reached."""
    pass

class RoleMatchError(Exception):
    """Role does not match with target role"""
    pass

class UserNotFoundError(Exception):
    """User not found."""
    pass

Role = Literal["student", "parent", "teacher", "system_admin"]
Role_Objects = Union[Student, Parent, Teacher, SystemAdmin]

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"[TIMER] {func.__name__} took {end - start:.3f} seconds")
        return result
    return wrapper

class CreationManager:
    # Main Methods
    def __init__(self, system_admin, config: CreationManagerConfig):
        self._save_path: str = config.DATABASE_PATH
        self._system_admin: SystemAdmin = system_admin
        self._users: list[User] = []
        self._config = config
        self._messages: list[MessageData] = []

    @timer
    def save(self):
        save_dir = os.path.split(self._save_path)[0]
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        """Save Function"""
        backup_file = self._save_path + ".bak"
        if os.path.exists(self._save_path):
            shutil.copy(self._save_path, backup_file)
        tmp_file = self._save_path + ".tmp"
        with open(tmp_file, "wb") as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            pickle.dump(self, f)
            portalocker.unlock(f)
        os.replace(tmp_file, self._save_path)

    @classmethod
    @timer
    def load(cls, path: str = "Database/cm3.pkl", system_admin = None, config = None):
        """Load Function, returns CreationManager object"""
        if not os.path.exists(path):
            if system_admin is None or config is None:
                return
            cm = cls(system_admin, config)
            cm.save()
            logger.info("New CreationManager created.")
            return cm
        with open(path, "rb") as f:
            portalocker.lock(f, portalocker.LOCK_SH)  # shared/read lock
            obj = pickle.load(f)
            portalocker.unlock(f)
        return obj

    # Get methods

    def get_user_by_username(self, username: str, role: Role = None) -> Role_Objects | User | None:
        """Get a User object by username property of that object"""
        for user in self._users:
            if user.username == username:
                # Username matches — now check role if specified
                if role is not None and user.role != role:
                    raise RoleMatchError(f"Role does not match. (Target: {role}, Found: {user.role})")
                return user

        if username == self._system_admin.username:
            return self._system_admin

        logger.error("Couldn't find user in Creation Manager.")
        return None

    def get_objective_by_code(self, code: int) -> str | None:
        for ol in self.config.HIGH_SCHOOL_OBJECTIVES.objectives.values():
            for o in ol:
                if str(o.code) == code: return o.objective
        return None

    def get_turkish_subject(self, subject_en: str):
        for subject in self.config.AVAILABLE_SUBJECTS:
            if subject.key == subject_en: return subject.name
        return None


    # Message Methods

    def get_user_message_data(self, user: User) -> list[MessageData]:
        return [msg for msg in self._messages if user in msg.contacts]

    def get_user_message_data_jsonized(self, user: User) -> list[dict]:
        return [msg.jsonized for msg in self._messages if user in msg.contacts]

    def get_md_by_id(self, md_id: int | str) -> MessageData | None:
        if isinstance(md_id, str):
            try:
                md_id = int(md_id)
            except ValueError:
                logger.error("Not a valid integer.")
                return None
        for md in self._messages:
            if md.id == md_id: return md
        return None

    def get_message_data(self, user: User, user2: User) -> MessageData | None:
        for msg in self.get_user_message_data(user):
            if user in msg.contacts and user2 in msg.contacts:
                return msg
        return None

    def get_user_contact_data(self, user: User) -> list[str]:
        contacts: list[str] = []
        for md in self.get_user_message_data(user):
            for contact in md.contacts:
                if contact != user: contacts.append(contact)
        return contacts

    def new_message(self, message: str, md: MessageData, from_who: User):
        if md is None:
            logger.error("MessageData is None")
            return False
        md.add_message(Message(message, from_who))
        self.save()
        return True

    # Utility Methods

    @staticmethod
    def username_must_not_exist(func):
        def wrapper(self, username, *args, **kwargs):
            if self.check_username_exists(username):
                logger.error(f"Username already exists: {username}")
                return
            return func(self, username, *args, **kwargs)

        return wrapper

    def check_user_limit(self, role: str = None) -> bool:
        """Check if anymore users can be created or not"""
        if role is None: return len(self._users) < self.config.MAX_USERS
        elif role == "student": return len(self.students) < self.config.MAX_STUDENTS
        elif role == "teacher": return len(self.teachers) < self.config.MAX_TEACHERS
        return False

    def auto_generate_username(self, name: str, surname: str):
        # Combine and lowercase
        base = (name + surname).lower()

        # Convert Turkish characters to English equivalents
        translations = str.maketrans({
            "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u"
        })
        base = base.translate(translations)

        # Normalize and remove any accent marks (for broader Unicode safety)
        base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")

        # Remove all characters except letters and numbers
        base = re.sub(r'[^a-z0-9]', '', base)

        existing_usernames = [user.username.lower() for user in self.users]

        # Handle duplicates by adding numbers
        username = base
        index = 0
        while username in existing_usernames:
            index += 1
            username = f"{base}{index}"

        return username

    def auto_generate_password(self, length=12, use_special_chars=False):
        """
        Automatically generate a password with uppers, lowers and digits by default.

        Special characters are optional
        Default length is 12
        """
        if length < 3:
            raise ValueError("Length must be at least 3 to include lower, upper, and digit.")
        if use_special_chars and length < 4:
            raise ValueError("Length must be at least 4 to include lower, upper, digit, and special char.")

        lower = secrets.choice(string.ascii_lowercase)
        upper = secrets.choice(string.ascii_uppercase)
        digit = secrets.choice(string.digits)
        password_chars = [lower, upper, digit]

        special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
        if use_special_chars:
            password_chars.append(secrets.choice(special_chars))

        all_chars = string.ascii_letters + string.digits + (special_chars if use_special_chars else "")
        remaining_length = length - len(password_chars)
        password_chars += [secrets.choice(all_chars) for _ in range(remaining_length)]

        secrets.SystemRandom().shuffle(password_chars)
        return "1234" # TEMPORARY
        return ''.join(password_chars)

    # Creation Methods

    def create_teacher(self, name: str, surname: str, gender: str, config: TeacherConfig):
        """Create a teacher"""
        if not self.check_user_limit("teacher"): raise GlobalLimitReachedError("Maximum teacher limit reached.")
        teacher = Teacher(self.auto_generate_username(name, surname), self.auto_generate_password(8, False), name, surname, gender, config)
        self._users.append(teacher)
        self._messages.append(MessageData([self._system_admin, teacher]))
        self.save()

    def create_parent(self, parent: Parent):
        if not self.check_user_limit(): return
        self._users.append(parent)
        self.save()

    def create_student(self, name: str, surname: str, gender: str, grade: int, teacher: Teacher, parents: list[ParentInformation]):
        """Create a student"""
        if not self.check_user_limit("student"): return False
        if not teacher.check_student_availability(): return False
        new_student = Student(self.auto_generate_username(name, surname), self.auto_generate_password(8, False), name, surname, gender, grade, teacher)
        self._messages.append(MessageData([teacher, new_student]))
        self._users.append(new_student)
        for pi in parents:
            p = Parent(self.auto_generate_username(pi.name, pi.surname), self.auto_generate_password(), pi.name, pi.surname, pi.gender, new_student, pi.relation)
            new_student.add_parent(p)
            self.create_parent(p)
        if teacher.check_student_availability():
            teacher.create_student(new_student)
            self.save()
        return True

    def change_user_settings(self, user: User, theme: str, language: str, notifications: bool):
        user.change_theme(theme)
        user.change_language(language)
        user.change_notifications(notifications)
        self.save()

    # Student Methods
    def add_student_homework(self, student: Student, title: str, description: str, start_date: CustomDate, end_date: CustomDate, subject: str, objective: str, num_questions: int):
        logger.info("Adding student homework.")
        student.add_homework(title, description, start_date, end_date, subject, objective, num_questions)
        self.save()

    # Properties

    @property
    def users(self):
        """Returns a list of all users"""
        return self._users
    @property
    def students(self):
        """Returns a list of users with role: student"""
        return [user for user in self._users if user.role == "student"]
    @property
    def teachers(self):
        """Returns a list of users with role: teacher"""
        return [user for user in self._users if user.role == "teacher"]
    @property
    def parents(self):
        """Returns a list of users with role: parent"""
        return [user for user in self._users if user.role == "parent"]
    @property
    def admin(self):
        """Returns the single SystemAdmin object"""
        return self._system_admin
    @property
    def config(self):
        """Returns the config as CreationManagerConfig"""
        return self._config
    @property
    def messages(self):
        return self._messages
    @property
    def available_modules(self):
        return self._config.AVAILABLE_MODULES

    # Role-Feature Mapping Method

    def get_features_by_role(self, role):
        role_feature_mappings = {
            "student": [
                {"name": "🏠 Ana Sayfa", "endpoint": "common_routes.dashboard_page"},
                {"name": "✉️ Mesajlar", "endpoint": "common_routes.messaging_page"},
                {"name": "📚 Derslerim", "endpoint": "student_routes.program_page"},
                {"name": "📖 Ödevlerim", "endpoint": "student_routes.homeworks_page"},
                {"name": "⚙️ Ayarlar", "endpoint": "common_routes.settings_page"},
                {"name": "🚪 Çıkış", "endpoint": "#", "onclick": "showLogoutModal()"}
            ],
            "parent": [
                {"name": "🏠 Ana Sayfa", "endpoint": "common_routes.dashboard_page"},
                {"name": "✉️ Mesajlar", "endpoint": "common_routes.messaging_page"},
                {"name": "📚 Dersler", "endpoint": "parent_routes.program_page"},
                {"name": "📖 Ödevler", "endpoint": "parent_routes.homework_page"},
                {"name": "⚙️ Ayarlar", "endpoint": "common_routes.settings_page"},
                {"name": "🚪 Çıkış", "endpoint": "#", "onclick": "showLogoutModal()"}
            ],
            "teacher": [
                {"name": "🏠 Ana Sayfa", "endpoint": "common_routes.dashboard_page"},
                {"name": "✉️ Mesajlar", "endpoint": "common_routes.messaging_page"},
                {"name": "🗃️ Programım", "endpoint": "teacher_routes.plan_program_page"},
                {"name": "🧑‍🎓 Öğrencilerim", "endpoint": "teacher_routes.students_page"},
                {"name": "➕ Yeni Öğrenci", "endpoint": "teacher_routes.create_student_page"},
                {"name": "⚙️ Ayarlar", "endpoint": "common_routes.settings_page"},
                {"name": "🚪 Çıkış", "endpoint": "#", "onclick": "showLogoutModal()"}
            ],
            "system_admin": [
                {"name": "🏠 Dashboard", "endpoint": "admin_routes.dashboard_page"},
                {"name": "✉️ Messages", "endpoint": "common_routes.messaging_page"},
                {"name": "🛡️ Admin Panel", "endpoint": "admin_routes.admin_panel"},
                {"name": "➕ Create Teacher", "endpoint": "admin_routes.create_teacher_page"},
                {"name": "🤖 Users", "endpoint": "admin_routes.users_page"},
                {"name": "🧑‍🎓 Students", "endpoint": "admin_routes.students_page"},
                {"name": "👨‍🏫 Teachers", "endpoint": "admin_routes.teachers_page"},
                {"name": "⚙️ Settings", "endpoint": "common_routes.settings_page"},
                {"name": "🚪 Logout", "endpoint": "#", "onclick": "showLogoutModal()"}
            ]
        }


        if role not in role_feature_mappings.keys():
            logger.error(f"Role not found (From CreationManager role mappings): {role}")
            return []

        return role_feature_mappings.get(role)