"""Unit tests for app.services.blockchain_service.

These don't require a live chain - Web3 connections are mocked. For a
real, live-node end-to-end check of the whole stack (deploy a contract,
read it back, send a transaction), see code/blockchain's own test suite
plus a manual run against `hardhat node`; this file is about the
service's own logic: deployment/ABI file discovery, error handling, and
the small pure-function helpers.
"""

import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from app.core.config import Settings
from app.services.blockchain_service import (
    BlockchainService,
    ContractNotDeployedError,
    WriteNotConfiguredError,
    is_read_only_function,
    json_safe,
)


@pytest.fixture()
def deployments_dir(tmp_path):
    """A fake blockchain/deployments/ directory with one deployed network."""
    abis_dir = tmp_path / "abis"
    abis_dir.mkdir()

    (tmp_path / "localhost.json").write_text(
        json.dumps(
            {
                "network": "localhost",
                "chainId": 31337,
                "contracts": {
                    "TestToken": "0x1111111111111111111111111111111111111111",
                    "TokenizedAsset": "0x2222222222222222222222222222222222222222",
                },
                "deployer": "0x3333333333333333333333333333333333333333",
            }
        )
    )
    (abis_dir / "TestToken.json").write_text(
        json.dumps(
            {
                "contractName": "TestToken",
                "abi": [
                    {
                        "type": "function",
                        "name": "name",
                        "inputs": [],
                        "outputs": [{"type": "string"}],
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
                ],
                "bytecode": "0x600160005500",
            }
        )
    )
    return tmp_path


@pytest.fixture()
def service(deployments_dir) -> BlockchainService:
    settings = Settings(
        SECRET_KEY="test-secret-key-that-is-at-least-32-chars!!",
        API_SECRET_KEY="test-api-secret-key-min-32-chars-here!!",
        DATABASE_URL="sqlite:///:memory:",
        BLOCKCHAIN_NETWORK="localhost",
        BLOCKCHAIN_DEPLOYMENTS_DIR=str(deployments_dir),
    )
    return BlockchainService(settings=settings)


# ── Deployment / ABI discovery ──────────────────────────────────────────────


def test_load_deployment_returns_manifest(service):
    deployment = service.load_deployment()
    assert deployment["chainId"] == 31337
    assert deployment["contracts"]["TestToken"].startswith("0x1111")


def test_load_deployment_missing_network_returns_none(service):
    assert service.load_deployment("sepolia") is None


def test_load_deployment_is_cached(service):
    first = service.load_deployment()
    # Mutate the cache directly to prove the second call doesn't re-read disk
    service._deployment_cache["localhost"] = {"contracts": {"cached": True}}
    second = service.load_deployment()
    assert second is not first
    assert second["contracts"] == {"cached": True}


def test_get_known_contract_address(service):
    assert service.get_known_contract_address("TestToken") == (
        "0x1111111111111111111111111111111111111111"
    )
    assert service.get_known_contract_address("NoSuchContract") is None


def test_known_contracts_empty_when_not_deployed(service):
    assert service.known_contracts("sepolia") == {}


def test_load_abi_and_bytecode(service):
    abi = service.load_abi("TestToken")
    assert any(fn["name"] == "mint" for fn in abi)
    assert service.load_bytecode("TestToken") == "0x600160005500"


def test_load_abi_missing_contract_returns_none(service):
    assert service.load_abi("NoSuchContract") is None
    assert service.load_bytecode("NoSuchContract") is None


# ── Error paths ──────────────────────────────────────────────────────────────


def test_send_contract_transaction_without_private_key_raises(service):
    with pytest.raises(WriteNotConfiguredError):
        service.send_contract_transaction(
            "0x1111111111111111111111111111111111111111",
            service.load_abi("TestToken"),
            "mint",
            ["0x2222222222222222222222222222222222222222", 1],
        )


def test_deploy_contract_without_private_key_raises(service):
    with pytest.raises(WriteNotConfiguredError):
        service.deploy_contract(
            service.load_abi("TestToken"), service.load_bytecode("TestToken")
        )


def test_deploy_known_contract_rejects_unknown_type(service):
    from app.services.blockchain_service import BlockchainServiceError

    with pytest.raises(BlockchainServiceError):
        service.deploy_known_contract("NotARealContract")


def test_deploy_known_contract_missing_artifact_raises(service):
    # "TokenizedAsset" is in the deployment manifest but we never wrote an
    # ABI/bytecode file for it in the fixture - should fail before even
    # checking for a configured signer.
    with pytest.raises(ContractNotDeployedError):
        service.deploy_known_contract("TokenizedAsset")


def test_get_tokenized_asset_details_missing_abi_raises(service):
    with pytest.raises(ContractNotDeployedError):
        service.get_tokenized_asset_details(
            "0x2222222222222222222222222222222222222222"
        )


# ── Connection handling ──────────────────────────────────────────────────────


def test_is_connected_false_on_exception(service):
    with patch.object(service, "get_web3", side_effect=RuntimeError("boom")):
        assert service.is_connected() is False


def test_get_web3_is_cached(service):
    with patch("app.services.blockchain_service.Web3") as MockWeb3:
        MockWeb3.HTTPProvider.return_value = MagicMock()
        MockWeb3.return_value = MagicMock()
        w3_a = service.get_web3("localhost")
        w3_b = service.get_web3("localhost")
        assert w3_a is w3_b
        assert MockWeb3.call_count == 1


# ── Pure helper functions ────────────────────────────────────────────────────


def test_is_read_only_function_view():
    abi = [{"type": "function", "name": "balanceOf", "stateMutability": "view"}]
    assert is_read_only_function(abi, "balanceOf") is True


def test_is_read_only_function_nonpayable():
    abi = [{"type": "function", "name": "transfer", "stateMutability": "nonpayable"}]
    assert is_read_only_function(abi, "transfer") is False


def test_is_read_only_function_unknown_defaults_to_write():
    abi = [{"type": "function", "name": "transfer", "stateMutability": "nonpayable"}]
    # Fail closed: an unrecognized function name is treated as a write so
    # callers don't accidentally skip requiring a signer.
    assert is_read_only_function(abi, "doesNotExist") is False


def test_json_safe_converts_bytes_and_nested_structures():
    assert json_safe(b"\x01\x02") == "0x0102"
    assert json_safe((1, "a", b"\xff")) == [1, "a", "0xff"]
    assert json_safe({"x": Decimal("1.5")}) == {"x": "1.5"}
    assert json_safe([1, [2, 3]]) == [1, [2, 3]]
    assert json_safe(42) == 42
