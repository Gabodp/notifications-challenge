from abc import ABC, abstractmethod

from app.models import Notification


class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, notification: Notification) -> None:
        pass


class EmailNotificationStrategy(NotificationStrategy):
    def send(self, notification: Notification) -> None:
        print(notification.channel)


class SMSNotificationStrategy(NotificationStrategy):
    def send(self, notification: Notification) -> None:
        print(notification.channel)


class PushNotificationStrategy(NotificationStrategy):
    def send(self, notification: Notification) -> None:
        print(notification.channel)
