from typing import Annotated

from fastapi import Depends

from app.services.notification_service import NotificationService
from app.strategy.notification_strategy import (
    EmailNotificationStrategy,
    PushNotificationStrategy,
    SMSNotificationStrategy,
)
from app.strategy.strategy_selector import NotificationStrategySelector


def get_strategy_selector() -> NotificationStrategySelector:
    return NotificationStrategySelector(
        email_strategy=EmailNotificationStrategy(),
        sms_strategy=SMSNotificationStrategy(),
        push_strategy=PushNotificationStrategy(),
    )


def get_notification_service(
    selector: Annotated[NotificationStrategySelector, Depends(get_strategy_selector)],
) -> NotificationService:
    return NotificationService(strategy_selector=selector)
