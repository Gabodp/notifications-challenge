from pydantic import BaseModel, ConfigDict, Field, EmailStr
from enums import Channel


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)
    name: str = Field(min_length=1, max_length=50)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    name: str
    

class NotificationBase(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    content: str = Field(max_length=150)
    channel: Channel 


class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    channel: Channel
    sender: UserResponse