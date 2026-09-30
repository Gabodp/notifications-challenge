from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models
from app.core.auth import CurrentUser
from app.core.database import get_db
from app.enums import Entity
from app.helpers import action_not_authorized, entity_not_found_exception
from app.notification_factory import NotificationModelFactory
from app.schemas import (
    AnyNotificationCreate,
    AnyNotificationUpdate,
    NotificationResponse,
)

router = APIRouter()


@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Notification).options(selectinload(models.Notification.sender))
    )
    return result.scalars().all()


@router.get("/{notification_id}/", response_model=NotificationResponse)
async def get_notification(
    notification_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Notification)
        .options(selectinload(models.Notification.sender))
        .where(models.Notification.id == notification_id)
    )

    notification = result.scalars().first()
    if not notification:
        entity_not_found_exception(Entity.NOTIFICATION)

    return notification


@router.post(
    "/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED
)
async def create_notification(
    notification: AnyNotificationCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    notification_to_persist = NotificationModelFactory.create_from_schema(
        notification, current_user.id
    )

    db.add(notification_to_persist)
    await db.commit()
    await db.refresh(notification_to_persist)
    await db.refresh(notification_to_persist, attribute_names=["sender"])

    return notification_to_persist


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_data: AnyNotificationUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Notification).where(models.Notification.id == notification_id)
    )
    notification = result.scalars().first()

    if not notification:
        entity_not_found_exception(Entity.NOTIFICATION)

    if current_user.id != notification.user_id:
        action_not_authorized(Entity.NOTIFICATION)

    if notification_data.channel != notification.channel.value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The notification channel cannot be changed",
        )

    update_data = notification_data.model_dump(exclude_unset=True, exclude={"channel"})
    for field, value in update_data.items():
        setattr(notification, field, value)

    await db.commit()
    await db.refresh(notification, attribute_names=["sender"])
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Notification).where(models.Notification.id == notification_id)
    )
    notification = result.scalars().first()

    if not notification:
        entity_not_found_exception(Entity.NOTIFICATION)

    if current_user.id != notification.user_id:
        action_not_authorized(Entity.NOTIFICATION)

    await db.delete(notification)
    await db.commit()
