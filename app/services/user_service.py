from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models
from app.core.auth import create_access_token, hash_password, verify_password
from app.core.config import settings
from app.enums import Entity
from app.helpers import (
    action_not_authorized,
    entity_already_exists_exception,
    entity_not_found_exception,
)
from app.schemas import Token, UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: UserCreate) -> models.User:
        result = await self.db.execute(
            select(models.User).where(
                func.lower(models.User.username) == payload.username.lower()
            )
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        result = await self.db.execute(
            select(models.User).where(
                func.lower(models.User.email) == payload.email.lower()
            )
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = models.User(
            name=payload.name,
            username=payload.username,
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def authenticate(self, email: str, password: str) -> Token:
        result = await self.db.execute(
            select(models.User).where(func.lower(models.User.email) == email.lower())
        )
        user = result.scalars().first()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=expires,
        )

        return Token(access_token=access_token, token_type="bearer")

    async def get(self, user_id: int) -> models.User:
        result = await self.db.execute(
            select(models.User).where(models.User.id == user_id)
        )
        user = result.scalars().first()

        if not user:
            entity_not_found_exception(Entity.USER)

        return user

    async def update(
        self,
        user_id: int,
        payload: UserUpdate,
        current_user_id: int,
    ) -> models.User:
        if current_user_id != user_id:
            action_not_authorized(Entity.USER)

        user = await self.get(user_id)

        if (
            payload.username is not None
            and payload.username.lower() != user.username.lower()
        ):
            result = await self.db.execute(
                select(models.User).where(
                    func.lower(models.User.username) == payload.username.lower()
                )
            )
            if result.scalars().first():
                entity_already_exists_exception(Entity.USERNAME)

            user.username = payload.username

        if payload.email is not None and payload.email.lower() != user.email.lower():
            result = await self.db.execute(
                select(models.User).where(
                    func.lower(models.User.email) == payload.email.lower()
                )
            )
            if result.scalars().first():
                entity_already_exists_exception(Entity.EMAIL)

            user.email = payload.email.lower()

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_notifications(self, user_id: int):
        await self.get(user_id)

        result = await self.db.execute(
            select(models.Notification)
            .options(selectinload(models.Notification.sender))
            .where(models.Notification.user_id == user_id)
        )
        return result.scalars().all()

    async def delete(self, user_id: int, current_user_id: int) -> None:
        if current_user_id != user_id:
            action_not_authorized(Entity.USER)

        user = await self.get(user_id)
        await self.db.delete(user)
        await self.db.commit()
