from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine, get_db
from app.dependencies import NotificationServiceDependency, UserServiceDependency
from app.routers import notifications, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


app.include_router(
    notifications.router, prefix="/api/notifications", tags=["notifications"]
)
app.include_router(users.router, prefix="/api/users", tags=["users"])


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    response.headers["X-Content-Type-Options"] = "nosniff"

    if "Referrer-Policy" not in response.headers:
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    if request.url.hostname not in ("localhost", "127.0.0.1"):
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )

    return response


@app.get("/health")
async def health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    return {"status": "healthy"}


@app.get("/", include_in_schema=False, name="home")
@app.get("/notifications", include_in_schema=False, name="notifications")
async def home(request: Request, notification_service: NotificationServiceDependency):
    notifications = await notification_service.get_all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"notifications": notifications, "title": "Home"},
    )


@app.get("/notifications/{notification_id}", include_in_schema=False)
async def post_page(
    request: Request,
    notification_id: int,
    notification_service: NotificationServiceDependency,
):
    notification = await notification_service.get(notification_id)
    if notification:
        title = notification.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": notification, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/users/{user_id}/notifications", include_in_schema=False, name="user_posts")
async def user_notifications_page(
    request: Request,
    user_id: int,
    user_service: UserServiceDependency,
):
    user = await user_service.get(user_id)
    notifications = await user_service.get_notifications(user_id)
    return templates.TemplateResponse(
        request,
        "user_notifications.html",
        {
            "notifications": notifications,
            "user": user,
            "title": f"{user.username}'s Notifications",
        },
    )


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )


@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )
