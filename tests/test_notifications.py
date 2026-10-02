import pytest
from httpx import AsyncClient

from tests.conftest import (
    auth_header,
    create_test_notification_email,
    create_test_user,
    login_user,
)


@pytest.mark.anyio
async def test_get_notifications_empty(client: AsyncClient):
    response = await client.get("/api/notifications")

    assert response.status_code == 200
    data = response.json()

    assert data == []


@pytest.mark.anyio
async def test_get_notification_not_found(client: AsyncClient):
    response = await client.get("/api/notifications/999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_notification(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/api/notifications",
        json={
            "title": "Test title",
            "content": "Test content",
            "channel": "email",
            "target_email": "test@email.com",
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["user_id"] == user["id"]
    assert data["sender"]["username"] == user["username"]


@pytest.mark.anyio
async def test_create_notification_not_authenticated(client: AsyncClient):
    response = await client.post(
        "/api/notifications",
        json={
            "title": "Test title",
            "content": "Test content",
            "channel": "email",
            "target_email": "test@email.com",
        },
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"] == "Not authenticated"
    )  # Default response from FastAPI


@pytest.mark.anyio
async def test_update_notification(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/api/notifications",
        json={
            "title": "Test title",
            "content": "Test content",
            "channel": "email",
            "target_email": "test@email.com",
        },
        headers=headers,
    )

    notification_id = response.json()["id"]

    response = await client.patch(
        f"/api/notifications/{notification_id}",
        json={"title": "New title", "content": "New content"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["content"] == "New content"


@pytest.mark.anyio
async def test_update_notification_wrong_user(client: AsyncClient):
    await create_test_user(
        client,
        name="test1",
        username="test1",
        email="test1@example.com",
        password="password1",
    )
    token1 = await login_user(client, email="test1@example.com", password="password1")

    response = await client.post(
        "/api/notifications",
        json={
            "title": "Test title",
            "content": "Test content",
            "channel": "email",
            "target_email": "test@email.com",
        },
        headers=auth_header(token1),
    )
    notification_id = response.json()["id"]

    await create_test_user(
        client,
        name="test2",
        username="test2",
        email="test2@example.com",
        password="password2",
    )
    token2 = await login_user(client, email="test2@example.com", password="password2")

    response = await client.patch(
        f"/api/notifications/{notification_id}",
        json={"title": "New title", "content": "New content"},
        headers=auth_header(token2),
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"] == "Not authorized to edit/delete this notification"
    )


@pytest.mark.anyio
async def test_delete_notification_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    notification = await create_test_notification_email(client, token)
    notification_id = notification["id"]

    response = await client.delete(
        f"/api/notifications/{notification_id}", headers=auth_header(token)
    )
    assert response.status_code == 204
