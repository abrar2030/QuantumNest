import pytest
from httpx import AsyncClient
from datetime import datetime
from app.main import app, create_access_token
from app.models import models

# Test data
TEST_PORTFOLIO = {
    "name": "Test Portfolio",
    "description": "A test portfolio for testing"
}

TEST_ASSET = {
    "symbol": "BTC",
    "name": "Bitcoin",
    "type": "CRYPTO",
    "current_price": 50000.00
}

TEST_PORTFOLIO_ASSET = {
    "portfolio_id": 1,
    "asset_id": 1,
    "quantity": 1.5,
    "purchase_price": 45000.00,
    "purchase_date": datetime.now().isoformat()
}

@pytest.fixture
async def test_user_token():
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": "test@example.com"}, expires_delta=access_token_expires
    )
    return access_token

@pytest.mark.asyncio
async def test_create_portfolio(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/portfolio/",
            json=TEST_PORTFOLIO,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == TEST_PORTFOLIO["name"]
    assert data["description"] == TEST_PORTFOLIO["description"]

@pytest.mark.asyncio
async def test_read_portfolios(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/portfolio/",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_read_portfolio(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/portfolio/1",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == TEST_PORTFOLIO["name"]

@pytest.mark.asyncio
async def test_update_portfolio(test_user_token):
    updated_portfolio = TEST_PORTFOLIO.copy()
    updated_portfolio["name"] = "Updated Test Portfolio"
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/portfolio/1",
            json=updated_portfolio,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test Portfolio"

@pytest.mark.asyncio
async def test_add_asset_to_portfolio(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/portfolio/assets/",
            json=TEST_PORTFOLIO_ASSET,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == TEST_PORTFOLIO_ASSET["quantity"]
    assert data["purchase_price"] == TEST_PORTFOLIO_ASSET["purchase_price"]

@pytest.mark.asyncio
async def test_read_portfolio_asset(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/portfolio/assets/1",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["portfolio_id"] == TEST_PORTFOLIO_ASSET["portfolio_id"]
    assert data["asset_id"] == TEST_PORTFOLIO_ASSET["asset_id"]

@pytest.mark.asyncio
async def test_update_portfolio_asset(test_user_token):
    updated_asset = TEST_PORTFOLIO_ASSET.copy()
    updated_asset["quantity"] = 2.0
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/portfolio/assets/1",
            json=updated_asset,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 2.0

@pytest.mark.asyncio
async def test_get_portfolio_performance(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/portfolio/performance/1?period=1m",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "portfolio_id" in data
    assert "period" in data
    assert "return_percentage" in data
    assert "data_points" in data

@pytest.mark.asyncio
async def test_delete_portfolio_asset(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(
            "/portfolio/assets/1",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_portfolio(test_user_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(
            "/portfolio/1",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    assert response.status_code == 204 