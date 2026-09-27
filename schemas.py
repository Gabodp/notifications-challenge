from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from enums import Channel


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


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
    user_id: int


class NotificationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=50)
    content: str | None = Field(default=None, min_lenght=1, max_length=150)


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    channel: Channel
    sender: UserPublic
    date_created: datetime
