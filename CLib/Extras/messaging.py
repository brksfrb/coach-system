from dataclasses import dataclass, field
from .configs import Hour
from .date import get_now
from ..Users.user import User
from logger import logger


@dataclass
class Message:
    """
    Message class to store messages

    Attributes:
        message (str): The message as string, must be passed
        from_who (User): The user who sent the message
        time (Hour): The time the message was sent, in HH:MM, passed automatically
        sent (bool): Whether the message was sent or not, False by default
    """
    message: str
    from_who: User
    time: Hour = field(default_factory=get_now)
    sent: list[User] = field(default_factory=list)

class MessageData:
    """
    MessageData class to store Message objects

    """
    _id_counter = 0
    def __init__(self, contacts: list[User]):
        MessageData._id_counter += 1
        self._id = MessageData._id_counter

        self._contacts: list[User] = contacts
        self._messages: list[Message] = []

    def __repr__(self):
        return f"MessageData object with ID: {self._id}"

    def __setstate__(self, state: dict):
        """
        Restore the object's state when unpickled.
        Works even for older objects without _id.
        """
        # Directly restore everything
        self.__dict__.update(state)

        # If old pickled object had no _id, create one
        if not hasattr(self, "_id"):
            MessageData._id_counter += 1
            self._id = MessageData._id_counter

        # Sync the class-level counter
        if self._id > MessageData._id_counter:
            MessageData._id_counter = self._id

    @property
    def contacts(self):
        return self._contacts
    def contacts_except_username(self, username: str):
        for contact in self._contacts:
            if contact.username != username:
                return contact
        return None
    @property
    def contacts_as_username(self):
        return [c.username for c in self._contacts]
    @property
    def messages(self):
        return self._messages
    @property
    def id(self):
        return self._id

    @property
    def jsonized(self) -> dict:
        """
        Return a JSON-serializable representation of this MessageData object.
        """
        return {
            "id": self._id,
            "contacts_as_username": [user.username for user in self._contacts],
            "messages": [
                {
                    "message": msg.message,
                    "from_who": msg.from_who.username,
                    "time": str(msg.time),
                    "sent": [u.username for u in msg.sent],
                }
                for msg in self._messages
            ],
        }

    def add_message(self, message: Message) -> bool:
        if not isinstance(message, Message):
            raise ValueError("Must be Message object")
        if not message.from_who in self._contacts:
            logger.error("Contact not found.")
            return False
        self._messages.append(message)
        return True

    def get_message_for_contact(self, contact: User) -> tuple[list[Message], list[Message]]:
        return [msg for msg in self._messages if msg.from_who == contact], [msg for msg in self._messages if msg.from_who != contact]


    def get_unsent_messages(self, user: User) -> list[Message]:
        return [msg for msg in self._messages if not user in msg.sent]