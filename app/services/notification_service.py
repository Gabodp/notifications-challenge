from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models
from app.enums import Channel, Entity
from app.helpers import action_not_authorized, entity_not_found_exception
from app.models import Notification
from app.notification_factory import NotificationModelFactory
from app.schemas import AnyNotificationCreate, NotificationUpdate
from app.strategy.strategy_selector import NotificationStrategySelector


class NotificationService:
    def __init__(
        self, db: AsyncSession, strategy_selector: NotificationStrategySelector
    ):
        self.strategy_selector = strategy_selector
        self.db = db

    def send(self, notification: Notification) -> None:
        strategy = self.strategy_selector.select(notification.channel)

        strategy.send(notification)

    async def get(self, notification_id: int) -> Notification:
        result = await self.db.execute(
            select(models.Notification)
            .options(selectinload(models.Notification.sender))
            .where(models.Notification.id == notification_id)
        )

        notification = result.scalars().first()
        if not notification:
            entity_not_found_exception(Entity.NOTIFICATION)

        return notification

    async def create(
        self, payload: AnyNotificationCreate, user_id: int
    ) -> Notification:
        notification = NotificationModelFactory.create_from_schema(payload, user_id)

        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        await self.db.refresh(notification, attribute_names=["sender"])

        return notification

    async def update(
        self,
        notification_id: int,
        payload: NotificationUpdate,
        user_id: int,
    ) -> Notification:
        notification = await self.get(notification_id)

        if user_id != notification.user_id:
            action_not_authorized(Entity.NOTIFICATION)

        allowed_fields = {
            Channel.EMAIL: {"title", "content", "target_email"},
            Channel.SMS: {"title", "content", "target_phone_number"},
            Channel.PUSH: {"title", "content", "device_token"},
        }

        ## This should be move somwhere else. Maybe created from the models.keys - id?
        ## I am worried whenever we add a new property for a model, we just forget to add it here

        update_data = payload.model_dump(exclude_unset=True, exclude={"channel"})
        invalid_fields = update_data.keys() - allowed_fields[notification.channel]

        if invalid_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"Fields {invalid_fields} are not valid for channel {notification.channel.value}"
                ),
            )

        for field, value in update_data.items():
            setattr(notification, field, value)

        await self.db.commit()
        await self.db.refresh(notification, attribute_names=["sender"])

        return notification

    async def delete(self, notification_id: int, user_id: int) -> None:
        result = await self.db.execute(
            select(models.Notification).where(models.Notification.id == notification_id)
        )
        notification = result.scalars().first()

        if not notification:
            entity_not_found_exception(Entity.NOTIFICATION)

        if user_id != notification.user_id:
            action_not_authorized(Entity.NOTIFICATION)

        await self.db.delete(notification)
        await self.db.commit()
