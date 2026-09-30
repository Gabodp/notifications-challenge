from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
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
    db: Annotated[AsyncSession, Depends(get_db)],
    selector: Annotated[NotificationStrategySelector, Depends(get_strategy_selector)],
) -> NotificationService:
    return NotificationService(db=db, strategy_selector=selector)


NotificationServiceDependency = Annotated[
    NotificationService,
    Depends(get_notification_service),
]
