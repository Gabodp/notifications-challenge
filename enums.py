from enum import Enum, unique

@unique
class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"