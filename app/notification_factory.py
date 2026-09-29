from app.core.database import Base
from app.models import EmailNotification, PushNotification, SMSNotification
from app.schemas import AnyNotificationCreate

NOTIFICATION_REGISTRY: dict[str, type[Base]] = {
    "email": EmailNotification,
    "sms": SMSNotification,
    "push": PushNotification,
}


class NotificationModelFactory:
    @staticmethod
    def create_from_schema(payload: AnyNotificationCreate) -> Base:
        model_class = NOTIFICATION_REGISTRY.get(payload.channel)

        if not model_class:
            raise ValueError(
                f"The notification channel '{payload.channel}' is not registered."
            )

        model_data = payload.model_dump()
        model_data.pop("channel", None)

        return model_class(**model_data)
