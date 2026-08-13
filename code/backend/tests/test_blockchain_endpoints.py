"""Tests for app.api.blockchain.

The BlockchainService itself is mocked here (via patching
`app.api.blockchain.get_blockchain_service`) so these run fast and need no
live chain. See test_blockchain_service.py for the service's own unit
tests, and the manual live-node check described in the PR/README for a
genuine end-to-end run against a real Hardhat node.
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from app.services.blockchain_service import (
    ContractNotDeployedError,
    NetworkUnavailableError,
    WriteNotConfiguredError,
)
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _mock_service(**overrides):
    service = MagicMock()
    service.is_connected.return_value = True
    service.known_contracts.return_value = {}
    service.get_known_contract_address.return_value = None
    for key, value in overrides.items():
        setattr(service, key, value)
    return service


# ── /wallet/{address}/balance ────────────────────────────────────────────────


def test_wallet_balance_rejects_invalid_address(client: TestClient, auth_headers: dict):
    resp = client.get("/blockchain/wallet/not-an-address/balance", headers=auth_headers)
    assert resp.status_code == 400


def test_wallet_balance_returns_eth_balance(client: TestClient, auth_headers: dict):
    mock = _mock_service()
    mock.get_eth_balance.return_value = Decimal("3.5")
    address = "0x" + "1" * 40
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.get(f"/blockchain/wallet/{address}/balance", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["balances"]["ETH"]["balance"] == "3.5"
    assert "value_usd" not in body["balances"]["ETH"]  # no fabricated price data


def test_wallet_balance_includes_token_balance_when_deployed(
    client: TestClient, auth_headers: dict
):
    mock = _mock_service()
    mock.get_eth_balance.return_value = Decimal("1")
    token_address = "0x" + "2" * 40
    mock.get_known_contract_address.return_value = token_address
    mock.get_erc20_balance.return_value = {
        "symbol": "QNT",
        "balance": Decimal("100"),
        "raw_balance": 100 * 10**18,
        "decimals": 18,
    }
    address = "0x" + "1" * 40
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.get(f"/blockchain/wallet/{address}/balance", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["balances"]["QNT"]["balance"] == "100"


def test_wallet_balance_502_when_network_unreachable(
    client: TestClient, auth_headers: dict
):
    mock = _mock_service()
    mock.is_connected.return_value = False
    address = "0x" + "1" * 40
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.get(f"/blockchain/wallet/{address}/balance", headers=auth_headers)
    assert resp.status_code == 502


# ── /networks ────────────────────────────────────────────────────────────────


def test_supported_networks_reports_live_status(client: TestClient, auth_headers: dict):
    mock = _mock_service()
    mock.is_connected.side_effect = lambda network: network == "localhost"
    mock.known_contracts.side_effect = (
        lambda network: {"TestToken": "0xabc"} if network == "localhost" else {}
    )
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.get("/blockchain/networks", headers=auth_headers)
    assert resp.status_code == 200
    networks = {n["id"]: n for n in resp.json()["networks"]}
    assert networks["localhost"]["reachable"] is True
    assert networks["localhost"]["contracts_deployed"] is True
    assert networks["sepolia"]["reachable"] is False
    # No deprecated testnets in the response
    assert "goerli" not in networks


# ── POST /deploy/contract ────────────────────────────────────────────────────


def test_deploy_contract_requires_premium_tier(client: TestClient, auth_headers: dict):
    """Regression test: the tier check used to compare str(enum) (e.g.
    'UserTier.BASIC') against lowercase tier names and was effectively
    broken. This exercises the real (fixed) comparison for a basic-tier
    user, who should still be correctly rejected."""
    resp = client.post(
        "/blockchain/deploy/contract",
        headers=auth_headers,
        json={"contract_type": "TestToken"},
    )
    assert resp.status_code == 403


def test_deploy_contract_allows_premium_and_above(
    client: TestClient, admin_headers: dict, db_session: Session
):
    """Regression test: admin_user's tier ('enterprise') must actually be
    recognized as premium-or-above by the (fixed) tier comparison."""
    mock = _mock_service()
    mock.deploy_known_contract.return_value = {
        "status": "success",
        "tx_hash": "0x" + "a" * 64,
        "contract_address": "0x" + "b" * 40,
        "block_number": 5,
        "gas_used": 500000,
        "from_address": "0x" + "c" * 40,
        "abi": [{"type": "function", "name": "name", "stateMutability": "view"}],
    }
    mock.get_web3.return_value.eth.chain_id = 31337
    mock.load_bytecode.return_value = "0x600160005500"
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.post(
            "/blockchain/deploy/contract",
            headers=admin_headers,
            json={"contract_type": "TestToken", "name": "My Token"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["address"] == "0x" + "b" * 40
    mock.deploy_known_contract.assert_called_once_with("TestToken", [], "localhost")

    # A real DB row should have been created for it.
    from app.models.models import BlockchainTransaction, SmartContract

    db_contract = (
        db_session.query(SmartContract)
        .filter(SmartContract.address == "0x" + "b" * 40)
        .first()
    )
    assert db_contract is not None
    assert db_contract.name == "My Token"
    assert db_contract.is_verified is True

    db_tx = (
        db_session.query(BlockchainTransaction)
        .filter(BlockchainTransaction.contract_id == db_contract.id)
        .first()
    )
    assert db_tx is not None
    assert db_tx.status == "success"


def test_deploy_contract_requires_type_or_abi(
    client: TestClient, admin_headers: dict
):
    mock = _mock_service()
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.post(
            "/blockchain/deploy/contract", headers=admin_headers, json={}
        )
    assert resp.status_code == 400


def test_deploy_contract_503_when_no_signer_configured(
    client: TestClient, admin_headers: dict
):
    mock = _mock_service()
    mock.deploy_known_contract.side_effect = WriteNotConfiguredError("no key")
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.post(
            "/blockchain/deploy/contract",
            headers=admin_headers,
            json={"contract_type": "TestToken"},
        )
    assert resp.status_code == 503


# ── POST /execute/contract/{id} ──────────────────────────────────────────────


_MINIMAL_ABI = [
    {
        "type": "function",
        "name": "balanceOf",
        "inputs": [{"type": "address", "name": "owner"}],
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "mint",
        "inputs": [
            {"type": "address", "name": "to"},
            {"type": "uint256", "name": "amount"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
]


@pytest.fixture()
def registered_contract(db_session: Session):
    from app.models.models import SmartContract

    contract = SmartContract(
        address="0x" + "d" * 40,
        name="Registered Token",
        contract_type="TestToken",
        network="localhost",
        abi=_MINIMAL_ABI,
        is_active=True,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


def test_execute_contract_not_found(client: TestClient, auth_headers: dict):
    resp = client.post(
        "/blockchain/execute/contract/99999",
        headers=auth_headers,
        json={"function": "name"},
    )
    assert resp.status_code == 404


def test_execute_contract_read_function_does_not_require_signer(
    client: TestClient, auth_headers: dict, registered_contract
):
    """Read calls should work for a basic-tier user with no signer key -
    only deploy/write paths are gated."""
    mock = _mock_service()
    mock.call_read_function.return_value = 12345
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.post(
            f"/blockchain/execute/contract/{registered_contract.id}",
            headers=auth_headers,
            json={"function": "balanceOf", "args": ["0x" + "1" * 40]},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"] == 12345
    mock.send_contract_transaction.assert_not_called()


def test_execute_contract_write_function_persists_transaction(
    client: TestClient, auth_headers: dict, registered_contract, db_session: Session
):
    mock = _mock_service()
    mock.send_contract_transaction.return_value = {
        "tx_hash": "0x" + "e" * 64,
        "status": "success",
        "block_number": 10,
        "gas_used": 40000,
        "from_address": "0x" + "f" * 40,
        "to_address": registered_contract.address,
    }
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.post(
            f"/blockchain/execute/contract/{registered_contract.id}",
            headers=auth_headers,
            json={"function": "mint", "args": ["0x" + "1" * 40, 1000]},
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    mock.call_read_function.assert_not_called()

    from app.models.models import BlockchainTransaction

    db_tx = (
        db_session.query(BlockchainTransaction)
        .filter(BlockchainTransaction.tx_hash == "0x" + "e" * 64)
        .first()
    )
    assert db_tx is not None
    assert db_tx.contract_id == registered_contract.id


def test_execute_contract_write_503_when_no_signer(
    client: TestClient, auth_headers: dict, registered_contract
):
    mock = _mock_service()
    mock.send_contract_transaction.side_effect = WriteNotConfiguredError("no key")
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.post(
            f"/blockchain/execute/contract/{registered_contract.id}",
            headers=auth_headers,
            json={"function": "mint", "args": ["0x" + "1" * 40, 1000]},
        )
    assert resp.status_code == 503


# ── /tokenization/assets ─────────────────────────────────────────────────────


def test_enrich_tokenized_asset_derives_real_values_only():
    from app.api.blockchain import _enrich_tokenized_asset

    details = {
        "asset_symbol": "AAPL",
        "token_name": "QuantumNest Apple Stock Token",
        "asset_name": "Apple Inc.",
        "asset_value": 17500,  # $175.00
        "total_supply": "2000000",
    }
    enriched = _enrich_tokenized_asset(details)
    assert enriched["name"] == "QuantumNest Apple Stock Token"
    assert enriched["underlying_asset"] == "Apple Inc."
    assert enriched["price_per_token"] == 175.0
    assert enriched["market_cap"] == 175.0 * 2_000_000
    # Original fields are preserved, not replaced.
    assert enriched["asset_symbol"] == "AAPL"


def test_enrich_tokenized_asset_handles_missing_fields():
    from app.api.blockchain import _enrich_tokenized_asset

    enriched = _enrich_tokenized_asset({"asset_symbol": "AAPL"})
    assert enriched["price_per_token"] == 0
    assert enriched["market_cap"] == 0
    assert enriched["name"] is None


def test_tokenized_assets_empty_when_nothing_deployed(
    client: TestClient, auth_headers: dict
):
    mock = _mock_service()
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.get("/blockchain/tokenization/assets", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["data"] == []


def test_tokenized_assets_falls_back_to_known_deployment(
    client: TestClient, auth_headers: dict
):
    """With nothing registered in the DB, the endpoint should still find a
    TokenizedAsset if one is in the network's deployment manifest - this is
    what makes a freshly `npm run deploy`-ed chain show up automatically."""
    mock = _mock_service()
    asset_address = "0x" + "9" * 40
    mock.get_known_contract_address.side_effect = (
        lambda name, network=None: asset_address if name == "TokenizedAsset" else None
    )
    mock.get_tokenized_asset_details.return_value = {
        "asset_symbol": "AAPL",
        "token_symbol": "qAAPL",
        "token_name": "QuantumNest Apple Stock Token",
        "asset_name": "Apple Inc.",
        "asset_value": 18000,  # $180.00, in cents
        "total_supply": "1000000",
        "contract_address": asset_address,
    }
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.get("/blockchain/tokenization/assets", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    asset = body["data"][0]
    assert asset["asset_symbol"] == "AAPL"
    # Derived, frontend-friendly fields - real values, not fabricated.
    assert asset["name"] == "QuantumNest Apple Stock Token"
    assert asset["underlying_asset"] == "Apple Inc."
    assert asset["price_per_token"] == 180.0
    assert asset["market_cap"] == 180.0 * 1_000_000


def test_tokenized_assets_reports_per_contract_errors(
    client: TestClient, auth_headers: dict
):
    mock = _mock_service()
    asset_address = "0x" + "9" * 40
    mock.get_known_contract_address.side_effect = (
        lambda name, network=None: asset_address if name == "TokenizedAsset" else None
    )
    mock.get_tokenized_asset_details.side_effect = NetworkUnavailableError("rpc down")
    with patch("app.api.blockchain.get_blockchain_service", return_value=mock):
        resp = client.get("/blockchain/tokenization/assets", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert body["errors"][0]["contract_address"] == asset_address
