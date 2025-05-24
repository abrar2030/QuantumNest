import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.main import app, create_access_token
from app.models import models
from app.schemas import schemas
from datetime import timedelta

# Test data
TEST_USER = {
    "email": "test@example.com",
    "name": "Test User",
    "password": "testpass123",
    "role": "USER",
    "tier": "BASIC"
}

ADMIN_USER = {
    "email": "admin@example.com",
    "name": "Admin User",
    "password": "adminpass123",
    "role": "ADMIN",
    "tier": "PREMIUM"
}

@pytest.fixture
async def test_user_token():
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": TEST_USER["email"]}, expires_delta=access_token_expires
    )
    return access_token

@pytest.fixture
async def admin_user_token():
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": ADMIN_USER["email"]}, expires_delta=access_token_expires
    )
    return access_token

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/", json=TEST_USER)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER["email"]
    assert data["name"] == TEST_USER["name"]
    assert "password" not in data

@pytest.mark.asyncio
async def test_create_duplicate_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/", json=TEST_USER)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_read_users_me(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/users/me",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER["email"]

@pytest.mark.asyncio
async def test_read_users_unauthorized(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/users/",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_read_users_admin(admin_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/users/",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_read_user(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/users/1",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER["email"]

@pytest.mark.asyncio
async def test_update_user(test_user_token):
    updated_user = TEST_USER.copy()
    updated_user["name"] = "Updated Test User"
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/users/1",
            json=updated_user,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test User"

@pytest.mark.asyncio
async def test_delete_user_unauthorized(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(
            "/users/1",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_user_admin(admin_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(
            "/users/1",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )
    assert response.status_code == 204 