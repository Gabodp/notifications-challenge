from fastapi import FastAPI

from database import Base, engine
from routers import notifications, users

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(
    notifications.router, prefix="/api/notifications", tags=["notifications"]
)
app.include_router(users.router, prefix="/api/users", tags=["users"])
