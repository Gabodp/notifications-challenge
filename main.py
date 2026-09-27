from fastapi import FastAPI


from enums import Channel

app = FastAPI()


notifications = [
    {
        "id": 1,
        "title": "Notification de prueba",
        "content": "Este es un contenido de prueba",
        "channel": Channel.SMS
    }
]

@app.get("/api/notifications")
def get_notifications():
    return notifications
