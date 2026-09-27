
from fastapi import APIRouter
from enums import Channel

router = APIRouter()


notifications = [
    {
        "id": 1,
        "title": "Notification de prueba",
        "content": "Este es un contenido de prueba",
        "channel": Channel.SMS
    }
]

@router.get("/")
def get_notifications():
    return notifications