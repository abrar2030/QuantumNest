import pytest
from httpx import AsyncClient
from app.main import app

import asyncio

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to QuantumNest Capital API"}

@pytest.mark.asyncio
async def test_login_for_access_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 401  # Assuming test credentials are invalid 