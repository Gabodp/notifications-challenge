import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_user_not_found(client: AsyncClient):
    result = await client.get("/api/users/999")
    assert result.status_code == 404


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
