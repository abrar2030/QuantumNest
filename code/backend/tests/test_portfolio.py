"""Portfolio API endpoint tests."""

import pytest
from app.core.time_utils import utc_now
from app.models.models import Asset
from fastapi.testclient import TestClient

TEST_PORTFOLIO = {
    "name": "Test Portfolio",
    "description": "A test portfolio for testing",
    "risk_level": "moderate",
    "base_currency": "USD",
}


@pytest.fixture()
def portfolio_id(client: TestClient, auth_headers: dict) -> int:
    """Create a portfolio and return its id."""
    r = client.post("/portfolio/", json=TEST_PORTFOLIO, headers=auth_headers)
    assert r.status_code == 201, r.text
    return r.json()["id"]


@pytest.fixture()
def asset_id(db_session) -> int:
    """Create a test asset and return its id."""
    asset = Asset(
        symbol="BTC",
        name="Bitcoin",
        asset_type="crypto",
        currency="USD",
        is_active=True,
        is_tradable=True,
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset.id


def test_create_portfolio(client: TestClient, auth_headers: dict):
    r = client.post("/portfolio/", json=TEST_PORTFOLIO, headers=auth_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == TEST_PORTFOLIO["name"]
    assert data["description"] == TEST_PORTFOLIO["description"]


def test_read_portfolios(client: TestClient, auth_headers: dict, portfolio_id: int):
    r = client.get("/portfolio/", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(p["id"] == portfolio_id for p in data)


def test_read_portfolio(client: TestClient, auth_headers: dict, portfolio_id: int):
    r = client.get(f"/portfolio/{portfolio_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == TEST_PORTFOLIO["name"]


def test_update_portfolio(client: TestClient, auth_headers: dict, portfolio_id: int):
    updated = {**TEST_PORTFOLIO, "name": "Updated Test Portfolio"}
    r = client.put(f"/portfolio/{portfolio_id}", json=updated, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Test Portfolio"


def test_add_asset_to_portfolio(
    client: TestClient, auth_headers: dict, portfolio_id: int, asset_id: int
):
    payload = {
        "portfolio_id": portfolio_id,
        "asset_id": asset_id,
        "quantity": 1.5,
        "purchase_price": 45000.00,
        "purchase_date": utc_now().isoformat(),
    }
    r = client.post("/portfolio/assets/", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    data = r.json()
    assert float(data["quantity"]) == 1.5
    assert float(data["purchase_price"]) == 45000.0


def test_read_portfolio_asset(
    client: TestClient, auth_headers: dict, portfolio_id: int, asset_id: int
):
    payload = {
        "portfolio_id": portfolio_id,
        "asset_id": asset_id,
        "quantity": 1.5,
        "purchase_price": 45000.00,
        "purchase_date": utc_now().isoformat(),
    }
    r = client.post("/portfolio/assets/", json=payload, headers=auth_headers)
    assert r.status_code == 201
    pa_id = r.json()["id"]

    r2 = client.get(f"/portfolio/assets/{pa_id}", headers=auth_headers)
    assert r2.status_code == 200
    assert r2.json()["portfolio_id"] == portfolio_id
    assert r2.json()["asset_id"] == asset_id


def test_update_portfolio_asset(
    client: TestClient, auth_headers: dict, portfolio_id: int, asset_id: int
):
    payload = {
        "portfolio_id": portfolio_id,
        "asset_id": asset_id,
        "quantity": 1.5,
        "purchase_price": 45000.00,
        "purchase_date": utc_now().isoformat(),
    }
    r = client.post("/portfolio/assets/", json=payload, headers=auth_headers)
    assert r.status_code == 201
    pa_id = r.json()["id"]

    updated = {**payload, "quantity": 2.0}
    r2 = client.put(f"/portfolio/assets/{pa_id}", json=updated, headers=auth_headers)
    assert r2.status_code == 200
    assert float(r2.json()["quantity"]) == 2.0


def test_get_portfolio_performance(
    client: TestClient, auth_headers: dict, portfolio_id: int
):
    r = client.get(
        f"/portfolio/performance/{portfolio_id}?period=1m", headers=auth_headers
    )
    assert r.status_code == 200
    data = r.json()
    assert "portfolio_id" in data
    assert "period" in data
    assert "return_percentage" in data
    assert "data_points" in data


def test_get_portfolio_summary(
    client: TestClient, auth_headers: dict, portfolio_id: int
):
    r = client.get(f"/portfolio/summary/{portfolio_id}", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["portfolio_id"] == portfolio_id
    assert "total_assets" in data


def test_delete_portfolio_asset(
    client: TestClient, auth_headers: dict, portfolio_id: int, asset_id: int
):
    payload = {
        "portfolio_id": portfolio_id,
        "asset_id": asset_id,
        "quantity": 1.5,
        "purchase_price": 45000.00,
        "purchase_date": utc_now().isoformat(),
    }
    r = client.post("/portfolio/assets/", json=payload, headers=auth_headers)
    assert r.status_code == 201
    pa_id = r.json()["id"]

    r2 = client.delete(f"/portfolio/assets/{pa_id}", headers=auth_headers)
    assert r2.status_code == 204


def test_delete_portfolio(client: TestClient, auth_headers: dict, portfolio_id: int):
    r = client.delete(f"/portfolio/{portfolio_id}", headers=auth_headers)
    assert r.status_code == 204


def test_read_nonexistent_portfolio(client: TestClient, auth_headers: dict):
    r = client.get("/portfolio/999999", headers=auth_headers)
    assert r.status_code == 404


def test_unauthenticated_portfolio_access(client: TestClient):
    r = client.get("/portfolio/")
    assert r.status_code == 401
