from fastapi import FastAPI

from routers import notifications, users
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
