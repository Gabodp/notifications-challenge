import pytest
from httpx import AsyncClient

from tests.conftest import (
    create_test_notification_email,
    create_test_user,
    login_user,
)


@pytest.mark.anyio
async def test_notification_pages_empty(client: AsyncClient):
    for path in ("/", "/notifications"):
        response = await client.get(path)

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "No notifications yet." in response.text


@pytest.mark.anyio
async def test_notification_pages_show_created_notification(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    notification = await create_test_notification_email(
        client,
        token,
        title="A page notification",
        content="Rendered notification content",
    )

    for path in ("/", "/notifications"):
        response = await client.get(path)

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert notification["title"] in response.text
        assert notification["content"] in response.text
        assert user["username"] in response.text
        assert f"/notifications/{notification['id']}" in response.text


@pytest.mark.anyio
async def test_notification_detail_page(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    notification = await create_test_notification_email(client, token)

    response = await client.get(f"/notifications/{notification['id']}")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert notification["title"] in response.text
    assert notification["content"] in response.text


@pytest.mark.anyio
async def test_notification_detail_page_not_found(client: AsyncClient):
    response = await client.get("/notifications/999999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_user_notifications_page_is_public(client: AsyncClient):
    user = await create_test_user(client)
    response = await client.get(f"/users/{user['id']}/notifications")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert f"Notifications by {user['username']}" in response.text
    assert "No notifications by this user yet." in response.text


@pytest.mark.anyio
async def test_user_notifications_page_uses_requested_user(client: AsyncClient):
    await create_test_user(client, username="viewer", email="viewer@example.com")
    viewer_token = await login_user(client, email="viewer@example.com")
    await create_test_notification_email(
        client, viewer_token, title="Viewer notification"
    )

    requested_user = await create_test_user(
        client, username="requested", email="requested@example.com"
    )
    requested_token = await login_user(client, email="requested@example.com")
    await create_test_notification_email(
        client, requested_token, title="Requested notification"
    )

    response = await client.get(f"/users/{requested_user['id']}/notifications")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Notifications by requested" in response.text
    assert "Requested notification" in response.text
    assert "Viewer notification" not in response.text


@pytest.mark.anyio
async def test_user_notifications_page_not_found(client: AsyncClient):
    response = await client.get("/users/999999/notifications")

    assert response.status_code == 404


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("path", "page_title"),
    [
        ("/login", "Login"),
        ("/register", "Register"),
        ("/account", "Account"),
    ],
)
async def test_static_html_pages(client: AsyncClient, path: str, page_title: str):
    response = await client.get(path)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert f"<title>Notifications - {page_title}</title>" in response.text
