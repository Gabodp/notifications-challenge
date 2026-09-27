from fastapi import FastAPI

from routers import notifications

app = FastAPI()

app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

