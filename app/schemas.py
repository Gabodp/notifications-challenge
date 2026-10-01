from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.enums import Channel


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class UserPrivate(UserPublic):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class NotificationBase(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    content: str = Field(max_length=150)
    channel: Channel


class NotificationCreate(NotificationBase):
    pass


class EmailNotificationCreate(NotificationCreate):
    channel: Literal["email"]
    target_email: EmailStr = Field(max_length=120)


class SMSNotificationCreate(NotificationCreate):
    channel: Literal["sms"]
    target_phone_number: int


class PushNotificationCreate(NotificationCreate):
    channel: Literal["push"]
    device_token: str = Field(max_length=25)


class NotificationUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )  # Rejects request instead of silently ignoring extra fields

    title: str | None = Field(default=None, min_length=1, max_length=50)
    content: str | None = Field(default=None, min_length=1, max_length=150)
    target_email: EmailStr | None = None
    target_phone_number: int | None = None
    device_token: str | None = Field(default=None, min_length=1, max_length=25)


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    user_id: int
    channel: Channel
    sender: UserPublic
    date_created: datetime


AnyNotificationCreate = Annotated[
    EmailNotificationCreate | SMSNotificationCreate | PushNotificationCreate,
    Field(discriminator="channel"),
]
