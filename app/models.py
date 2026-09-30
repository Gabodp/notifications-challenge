from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums import Channel, Status


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(150), nullable=False)

    notifications: Mapped[list[Notification]] = relationship(
        back_populates="sender", cascade="all, delete-orphan"
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[Channel] = mapped_column(Enum(Channel), nullable=False)
    status: Mapped[Status] = mapped_column(
        Enum(Status, name="delivery_status"),
        default=Status.SCHEDULED,
        server_default=Status.SCHEDULED.name,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": "notifications",
        "polymorphic_on": channel,
    }

    sender: Mapped[User] = relationship(back_populates="notifications")


class EmailNotification(Notification):
    __tablename__ = "email_notifications"

    id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    target_email: Mapped[str] = mapped_column(String(120), nullable=False)

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": Channel.EMAIL,
    }


class SMSNotification(Notification):
    __tablename__ = "sms_notifications"

    id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"), primary_key=True, index=True
    )

    target_phone_number: Mapped[int] = mapped_column(Integer, nullable=False)

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": Channel.SMS,
    }


class PushNotification(Notification):
    __tablename__ = "push_notifications"

    id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    device_token: Mapped[str] = mapped_column(String(80), nullable=False)
    send_status: Mapped[str] = mapped_column(String(25), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": Channel.PUSH,
    }
