from enum import Enum, unique


@unique
class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


@unique
class Entity(Enum):
    NOTIFICATION = "notification"
    USER = "user"
    USERNAME = "username"
