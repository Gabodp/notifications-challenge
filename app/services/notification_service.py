from app.models import Notification
from app.strategy.strategy_selector import NotificationStrategySelector


class NotificationService:
    def __init__(self, strategy_selector: NotificationStrategySelector):
        self.strategy_selector = strategy_selector

    def send(self, notification: Notification):
        strategy = self.strategy_selector.select(notification.channel)

        strategy.send(notification)
