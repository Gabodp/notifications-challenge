from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import engine
from app.routers import notifications, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(
    notifications.router, prefix="/api/notifications", tags=["notifications"]
)
app.include_router(users.router, prefix="/api/users", tags=["users"])
