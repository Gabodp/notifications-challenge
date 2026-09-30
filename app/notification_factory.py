from app.models import (
    EmailNotification,
    Notification,
    PushNotification,
    SMSNotification,
)
from app.schemas import AnyNotificationCreate

NOTIFICATION_REGISTRY: dict[str, type[Notification]] = {
    "email": EmailNotification,
    "sms": SMSNotification,
    "push": PushNotification,
}


class NotificationModelFactory:
    @staticmethod
    def create_from_schema(
        payload: AnyNotificationCreate, user_id: int
    ) -> Notification:
        model_class = NOTIFICATION_REGISTRY.get(payload.channel)

        if not model_class:
            raise ValueError(
                f"The notification channel '{payload.channel}' is not registered."
            )

        model_data = payload.model_dump()
        model_data.pop("channel", None)

        return model_class(user_id=user_id, **model_data)
