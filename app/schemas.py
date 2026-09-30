from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

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

    @model_validator(mode="after")
    def reject_null_updates(self) -> Self:
        # Omitted fields are allowed, but explicitly sending null is not.
        # This will avoid 500 Internal errors by explicitly returning an explanation.
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class EmailNotificationUpdate(NotificationUpdate):
    channel: Literal["email"]
    target_email: EmailStr | None = Field(default=None, max_length=120)


class SMSNotificationUpdate(NotificationUpdate):
    channel: Literal["sms"]
    target_phone_number: int | None = None


class PushNotificationUpdate(NotificationUpdate):
    channel: Literal["push"]
    device_token: str | None = Field(default=None, min_length=1, max_length=25)


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    channel: Channel
    sender: UserPublic
    date_created: datetime


AnyNotificationUpdate = Annotated[
    EmailNotificationUpdate | SMSNotificationUpdate | PushNotificationUpdate,
    Field(discriminator="channel"),
]


AnyNotificationCreate = Annotated[
    EmailNotificationCreate | SMSNotificationCreate | PushNotificationCreate,
    Field(discriminator="channel"),
]
