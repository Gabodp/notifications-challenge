
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db

from schemas import NotificationResponse, UserCreate, UserResponse
from enums import Entity
from helpers import entity_not_found_exception
import models


router = APIRouter()



@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.username == user.username),
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    result = db.execute(
        select(models.User).where(models.User.email == user.email),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_user = models.User(
        name = user.name,
        username = user.username,
        email = user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/{user_id}/notifications", response_model=list[NotificationResponse])
def get_user_notifications(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    existing_user = result.scalars().first()
    if not existing_user:
        entity_not_found_exception(Entity.USER)
    
    result = db.execute(
        select(models.Notification).where(models.Notification.user_id == user_id)
    )
    notifications = result.scalars().all()

    return notifications