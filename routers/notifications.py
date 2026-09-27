
from typing import Annotated

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db

from schemas import NotificationCreate, NotificationResponse

import models

router = APIRouter()


@router.get("")
def get_notifications(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Notification))
    return result.scalars().all()

@router.post(
    "", 
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == notification.user_id)
    )

    user = result.scalars().first()
    if not user:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_notification = models.Notification(
        title = notification.title,
        content = notification.content,
        channel = notification.channel,
        user_id = notification.user_id,
        date_created = datetime.now
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification