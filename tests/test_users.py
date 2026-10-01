import pytest
from httpx import AsyncClient

from tests.conftest import (
    auth_header,
    create_test_notification_email,
    create_test_user,
    login_user,
)


@pytest.mark.anyio
async def test_get_user_not_found(client: AsyncClient):
    result = await client.get("/api/users/999")
    assert result.status_code == 404


@pytest.mark.anyio
async def test_get_user_success(client: AsyncClient):
    user = await create_test_user(client, email="test@example.com")

    user_id = user["id"]
    result = await client.get(f"/api/users/{user_id}")
    assert result.status_code == 200


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
        },
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "name": "Test",
            "username": "test",
            "email": "test@example.com",
            "password": "password",
        },
    )

    data = response.json()
    assert response.status_code == 201
    assert data["name"] == "Test"
    assert data["username"] == "test"
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_create_user_duplicate_email(client: AsyncClient):
    await create_test_user(client, email="test@example.com")

    response = await client.post(
        "/api/users",
        json={
            "name": "Test Nane",
            "username": "example",
            "email": "test@example.com",
            "password": "password",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.anyio
async def test_get_current_user(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.get("/api/users/me", headers=headers)

    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_current_user_not_authenticated(client: AsyncClient):
    response = await client.get("/api/users/me")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_update_user_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    user_id = user["id"]
    response = await client.patch(
        f"/api/users/{user_id}", json={"name": "New name"}, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New name"


@pytest.mark.anyio
async def test_update_different_user_failed(client: AsyncClient):
    user1 = await create_test_user(
        client, username="user1", email="user1@example.com", password="testpassword"
    )

    await create_test_user(
        client, username="user2", email="user2@example.com", password="testpassword"
    )
    token2 = await login_user(
        client, email="user2@example.com", password="testpassword"
    )

    user_id = user1["id"]
    response = await client.patch(
        f"/api/users/{user_id}", json={"name": "New name"}, headers=auth_header(token2)
    )

    assert response.status_code == 403


@pytest.mark.anyio
async def test_get_user_notifications(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    await create_test_notification_email(client, token)

    user_id = user["id"]
    response = await client.get(f"/api/users/{user_id}/notifications")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test title"
    assert response.json()[0]["channel"] == "email"
