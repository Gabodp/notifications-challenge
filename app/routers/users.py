from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import CurrentUser
from app.dependencies import UserServiceDependency
from app.schemas import (
    NotificationResponse,
    Token,
    UserCreate,
    UserPrivate,
    UserPublic,
    UserUpdate,
)

router = APIRouter()


@router.post(
    "",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, user_service: UserServiceDependency):
    return await user_service.create(user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserServiceDependency,
):
    return await user_service.authenticate(form_data.username, form_data.password)


@router.get("/me", response_model=UserPrivate)
async def get_current_user(current_user: CurrentUser):
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, user_service: UserServiceDependency):
    return await user_service.get(user_id)


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_partial_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: CurrentUser,
    user_service: UserServiceDependency,
):
    return await user_service.update(user_id, user_update, current_user.id)


@router.get("/{user_id}/notifications", response_model=list[NotificationResponse])
async def get_user_notifications(
    user_id: int,
    user_service: UserServiceDependency,
):
    return await user_service.get_notifications(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    user_service: UserServiceDependency,
):
    await user_service.delete(user_id, current_user.id)
