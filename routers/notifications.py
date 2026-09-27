from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from enums import Entity
from helpers import entity_not_found_exception
from schemas import NotificationCreate, NotificationResponse, NotificationUpdate

router = APIRouter()


@router.get("/", response_model=list[NotificationResponse])
def get_notifications(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Notification))
    return result.scalars().all()


@router.get("/{notification_id}/")
def get_notification(notification_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Notification).where(models.Notification.id == notification_id)
    )

    notification = result.scalars().first()
    if not notification:
        entity_not_found_exception(Entity.NOTIFICATION)

    return notification


@router.post(
    "/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED
)
def create_notification(
    notification: NotificationCreate, db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(
        select(models.User).where(models.User.id == notification.user_id)
    )

    user = result.scalars().first()
    if not user:
        entity_not_found_exception(Entity.USER)

    new_notification = models.Notification(
        title=notification.title,
        content=notification.content,
        channel=notification.channel,
        user_id=notification.user_id,
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


@router.patch("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(models.Notification).where(models.Notification.id == notification_id)
    )
    notification = result.scalars().first()

    if not notification:
        entity_not_found_exception(Entity.NOTIFICATION)

    update_data = notification_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification_data, field, value)

    db.commit()
    db.refresh(notification, attribute_names=["sender"])
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Notification).where(models.Notification.id == notification_id)
    )
    notification = result.scalars().first()

    if not notification:
        entity_not_found_exception(Entity.NOTIFICATION)

    db.delete(notification)
    db.commit()
