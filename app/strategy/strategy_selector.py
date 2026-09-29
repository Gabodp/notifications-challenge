from app.enums import Channel
from app.strategy.notification_strategy import (
    EmailNotificationStrategy,
    NotificationStrategy,
    PushNotificationStrategy,
    SMSNotificationStrategy,
)


class NotificationStrategySelector:
    def __init__(
        self,
        email_strategy: EmailNotificationStrategy,
        sms_strategy: SMSNotificationStrategy,
        push_strategy: PushNotificationStrategy,
    ):
        self.email_strategy = email_strategy
        self.sms_strategy = sms_strategy
        self.push_strategy = push_strategy

    def select(self, channel: Channel) -> NotificationStrategy:

        match channel:
            case Channel.EMAIL:
                return self.email_strategy

            case Channel.SMS:
                return self.sms_strategy

            case Channel.PUSH:
                return self.push_strategy

            case _:
                raise ValueError(f"Unsupported channel: {channel}")
