from enum import Enum, unique


@unique
class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


@unique
class Status(Enum):
    SCHEDULED = "scheduled"
    DELIVERED = "delivered"


@unique
class Entity(Enum):
    NOTIFICATION = "notification"
    USER = "user"
    USERNAME = "username"
    EMAIL = "email"
