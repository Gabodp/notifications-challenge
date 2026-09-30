from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models
from app.core.auth import CurrentUser
from app.core.database import get_db
from app.dependencies import NotificationServiceDependency
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
    notification_id: int,
    notification_service: NotificationServiceDependency,
):
    return await notification_service.get(notification_id)


@router.post(
    "/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED
)
async def create_notification(
    notification: AnyNotificationCreate,
    current_user: CurrentUser,
    notification_service: NotificationServiceDependency,
):
    return await notification_service.create(notification, current_user.id)


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_data: AnyNotificationUpdate,
    current_user: CurrentUser,
    notification_service: NotificationServiceDependency,
):
    return await notification_service.update(
        notification_id,
        notification_data,
        current_user.id,
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: CurrentUser,
    notification_service: NotificationServiceDependency,
):
    await notification_service.delete(notification_id, current_user.id)
