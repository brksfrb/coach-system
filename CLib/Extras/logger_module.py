from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogMessage:
    message: str
    color: str
    time: str

@dataclass
class LoggerConfig:
    print_to_console: bool = True
    save_to_file: bool = True


def now():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

class Logger:
    def __init__(self, directory: str):
        self._directory = directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._path = f"{self._directory}/log{timestamp}.txt"
        self._logs: list[LogMessage] = []
        self._config = LoggerConfig()

    def config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                raise AttributeError(f"Invalid config option: {key}")

    def error(self, msg: str):
        self._logs.append(LogMessage(msg, "red", now()))

    def warning(self, msg: str):
        self._logs.append(LogMessage(msg, "yellow", now()))

    def success(self, msg: str):
        self._logs.append(LogMessage(msg, "lime", now()))

    def fail(self, msg: str):
        self._logs.append(LogMessage(msg, "orange", now()))

    def info(self, msg: str):
        self._logs.append(LogMessage(msg, "white", now()))

    def status(self, msg: str):
        self._logs.append(LogMessage(msg, "cyan", now()))

    @property
    def logs(self):
        return self._logs