import datetime

from logger import logger

turkish_role_mappings = {
    "teacher": "Öğretmen",
    "student": "Öğrenci",
    "parent": "Veli",
    "system_admin": "System Admin"
}

class User:
    def __init__(self, username: str, password: str, name: str, surname: str, role: str, gender: str):
        self._username: str = username
        self._password: str = password
        self._name: str = name
        self._surname: str = surname
        self._role: str = role
        self._gender: str = gender
        self._notifications: bool = False
        self._language = "en"
        self._theme = "light"
        self._previous_passwords = []

    def __setstate__(self, state):
        # Restore state from pickled object
        self.__dict__.update(state)
        if not hasattr(self, "_notifications"):
            self._notifications = True

    @property
    def username(self):
        return self._username
    @property
    def password(self):
        return self._password
    @property
    def name(self):
        return self._name.capitalize()
    @property
    def surname(self):
        return self._surname.capitalize()
    @property
    def fullname(self):
        return f"{self.name} {self.surname}"
    @property
    def role(self):
        return self._role
    @property
    def role_turkish(self):
        return turkish_role_mappings.get(self._role, "?")
    @property
    def gender(self):
        return self._gender
    @property
    def notifications(self):
        return self._notifications
    @property
    def language(self):
        return self._language
    @property
    def theme(self):
        return self._theme

    def change_password(self, old_password: str, new_password: str):
        if self.password != old_password:
            logger.error("Password missmatch.")
            return
        self._password = new_password
        self._previous_passwords.append((old_password, datetime.datetime.now()))
    def change_notifications(self, new_condition: bool):
        if not isinstance(new_condition, bool):
            logger.error("Must be bool. (True or False)")
            return
        self._notifications = new_condition
    def change_theme(self, new_theme: str):
        self._theme = new_theme
    def change_language(self, new_language: str):
        self._language = new_language
