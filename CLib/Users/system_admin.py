from logger import logger

class SystemAdmin:
    def __init__(self, username, password, name, surname):
        self._username = username
        self.__password = password
        self._name = name
        self._surname = surname
        self._role = "system_admin"
        self._notifications: bool = False
        self._theme = "light"
        self._language = "en"
        self._gender = "Male"

    def __setstate__(self, state):
        # Restore state from pickled object
        self.__dict__.update(state)
        if not hasattr(self, "_notifications"):
            self._notifications = True
        if not hasattr(self, "_gender"):
            self._gender = "Male"

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self.__password

    @property
    def name(self):
        return self._name

    @property
    def surname(self):
        return self._surname

    @property
    def fullname(self):
        return self._name + " " + self._surname

    @property
    def gender(self):
        return self._gender

    @property
    def role(self):
        return self._role
    @property
    def notifications(self):
        return self._notifications
    @property
    def theme(self):
        return self._theme
    @property
    def language(self):
        return self._language
    def change_notifications(self, new_condition: bool):
        if not isinstance(new_condition, bool):
            logger.error("Must be bool. (True or False)")
            return
        self._notifications = new_condition
    def change_theme(self, new_theme: str):
        self._theme = new_theme
    def change_language(self, new_language: str):
        self._language = new_language

    def __repr__(self):
        return f"SystemAdmin object with username: {self._username}"
