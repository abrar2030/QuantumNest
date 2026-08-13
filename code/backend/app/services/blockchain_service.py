"""Web3 integration service.

Talks to a real Ethereum-compatible JSON-RPC node (a local Hardhat node in
dev/docker-compose, a public testnet/mainnet RPC in production) using the
contract addresses and ABIs produced by `code/blockchain`'s Hardhat project
(see `blockchain/deployments/`, written by `npm run deploy`).

Design principles:
  - Never fabricate on-chain data. If a contract isn't deployed for the
    configured network, or the node is unreachable, callers get a clear
    error/None instead of a plausible-looking made-up value.
  - Read-only calls (view/pure functions, balances) never require a
    configured signer. Anything that sends a transaction (writes state)
    requires `settings.PRIVATE_KEY` to be set, and raises
    `WriteNotConfiguredError` with a clear message if it isn't - this
    service does not accept a caller-supplied private key over the API.
"""

from __future__ import annotations

import json
import logging
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import Settings, get_settings
from web3 import Web3
from web3.exceptions import TimeExhausted, Web3Exception

logger = logging.getLogger(__name__)

# Order of TokenizedAsset.getAssetDetails()'s return tuple - see
# blockchain/contracts/TokenizedAsset.sol. Kept in one place so a contract
# change only needs updating here.
_ASSET_DETAILS_FIELDS = [
    "asset_symbol",
    "asset_name",
    "asset_type",
    "asset_value",
    "description",
    "issuer",
    "issuance_date",
    "maturity_date",
    "year_to_date_return",
    "last_valuation_date",
    "trading_enabled",
    "trading_fee",
]

# Minimal ABI fragment for reading balances/metadata off of *any* ERC20
# token, not just ones we have full ABIs for.
_ERC20_MIN_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
]

_NETWORK_RPC_SETTINGS = {
    # Local/dev chains all share ETHEREUM_RPC_URL; only the network *name*
    # (used to pick the deployments/<network>.json file) differs.
    "hardhat": "ETHEREUM_RPC_URL",
    "localhost": "ETHEREUM_RPC_URL",
    "docker": "ETHEREUM_RPC_URL",
    "sepolia": "ETHEREUM_RPC_URL",
    "polygon_amoy": "POLYGON_RPC_URL",
    "polygon": "POLYGON_RPC_URL",
    "bsc": "BSC_RPC_URL",
}

# The five contract types code/blockchain knows how to compile & deploy.
# Kept here (rather than only in Solidity land) so the API layer can
# validate a requested `contract_type` before touching web3 at all.
KNOWN_CONTRACT_TYPES = [
    "TestToken",
    "TokenizedAsset",
    "PortfolioManager",
    "TradingPlatform",
    "DeFiIntegration",
]


def json_safe(value: Any) -> Any:
    """Recursively convert a decoded web3 return value (which may contain
    bytes/HexBytes, tuples, or AttributeDicts) into something json.dumps
    (and Pydantic/FastAPI's JSON encoder) can handle directly."""
    if isinstance(value, (bytes, bytearray)):
        return "0x" + bytes(value).hex()
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, Decimal):
        return str(value)
    return value


def is_read_only_function(abi: List[dict], function_name: str) -> bool:
    """True if `function_name` is a view/pure function per the ABI (i.e.
    callable with `.call()` and no signer/gas needed), False if it's
    state-changing (nonpayable/payable, needs a signed transaction).
    Defaults to False (treat as a write) if the function isn't found, so
    callers fail closed rather than silently skipping a required signature.
    """
    for entry in abi:
        if entry.get("type") == "function" and entry.get("name") == function_name:
            return entry.get("stateMutability") in ("view", "pure")
    return False


class BlockchainServiceError(Exception):
    """Base class for blockchain service errors."""


class NetworkUnavailableError(BlockchainServiceError):
    """The configured RPC endpoint could not be reached."""


class ContractNotDeployedError(BlockchainServiceError):
    """No deployment record/ABI exists for the requested contract+network."""


class WriteNotConfiguredError(BlockchainServiceError):
    """A transaction-sending operation was attempted with no signer key set."""


class BlockchainService:
    """Thin, well-tested wrapper around web3.py for the contracts in
    code/blockchain. One instance is safe to reuse across requests; it
    caches Web3 connections, loaded ABIs and deployment manifests.
    """

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._w3_cache: Dict[str, Web3] = {}
        self._deployment_cache: Dict[str, Optional[dict]] = {}
        self._abi_cache: Dict[str, Optional[dict]] = {}

    # ── Connection ───────────────────────────────────────────────────────

    def _rpc_url_for_network(self, network: str) -> str:
        setting_name = _NETWORK_RPC_SETTINGS.get(network, "ETHEREUM_RPC_URL")
        return getattr(self.settings, setting_name)

    def get_web3(self, network: Optional[str] = None) -> Web3:
        network = network or self.settings.BLOCKCHAIN_NETWORK
        if network in self._w3_cache:
            return self._w3_cache[network]

        rpc_url = self._rpc_url_for_network(network)
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))
        self._w3_cache[network] = w3
        return w3

    def is_connected(self, network: Optional[str] = None) -> bool:
        try:
            return self.get_web3(network).is_connected()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Blockchain connectivity check failed: %s", exc)
            return False

    # ── Deployment / ABI discovery ──────────────────────────────────────

    def _deployments_dir(self) -> Path:
        return Path(self.settings.BLOCKCHAIN_DEPLOYMENTS_DIR)

    def load_deployment(self, network: Optional[str] = None) -> Optional[dict]:
        """Load blockchain/deployments/<network>.json, if present."""
        network = network or self.settings.BLOCKCHAIN_NETWORK
        if network in self._deployment_cache:
            return self._deployment_cache[network]

        path = self._deployments_dir() / f"{network}.json"
        if not path.exists():
            logger.warning(
                "No deployment file for network '%s' at %s - blockchain "
                "endpoints that need a deployed contract will report "
                "'not deployed' until `npm run deploy` has been run.",
                network,
                path,
            )
            self._deployment_cache[network] = None
            return None

        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to read deployment file %s: %s", path, exc)
            self._deployment_cache[network] = None
            return None

        self._deployment_cache[network] = data
        return data

    def load_abi(self, contract_name: str) -> Optional[List[dict]]:
        """Load blockchain/deployments/abis/<ContractName>.json, if present."""
        artifact = self._load_artifact(contract_name)
        return artifact.get("abi") if artifact else None

    def load_bytecode(self, contract_name: str) -> Optional[str]:
        """Load the deployment bytecode for one of the five known contract
        types, if present. Used to deploy *new* instances of a known
        contract type via the API without the backend needing its own
        Solidity toolchain."""
        artifact = self._load_artifact(contract_name)
        return artifact.get("bytecode") if artifact else None

    def _load_artifact(self, contract_name: str) -> Optional[dict]:
        if contract_name in self._abi_cache:
            return self._abi_cache[contract_name]

        path = self._deployments_dir() / "abis" / f"{contract_name}.json"
        if not path.exists():
            logger.warning(
                "No exported artifact found for %s at %s", contract_name, path
            )
            self._abi_cache[contract_name] = None
            return None

        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to read artifact file %s: %s", path, exc)
            self._abi_cache[contract_name] = None
            return None

        self._abi_cache[contract_name] = data
        return data

    def get_known_contract_address(
        self, contract_name: str, network: Optional[str] = None
    ) -> Optional[str]:
        """Address of one of the five core contracts for `network`, per the
        deployment manifest, or None if not deployed there."""
        deployment = self.load_deployment(network)
        if not deployment:
            return None
        return deployment.get("contracts", {}).get(contract_name)

    def known_contracts(self, network: Optional[str] = None) -> Dict[str, str]:
        """All core contract addresses deployed for `network` (may be empty)."""
        deployment = self.load_deployment(network)
        if not deployment:
            return {}
        return dict(deployment.get("contracts", {}))

    # ── Contract helpers ─────────────────────────────────────────────────

    def get_contract(
        self, address: str, abi: List[dict], network: Optional[str] = None
    ):
        w3 = self.get_web3(network)
        return w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

    def call_read_function(
        self,
        address: str,
        abi: List[dict],
        function_name: str,
        args: Optional[list] = None,
        network: Optional[str] = None,
    ) -> Any:
        """Call a view/pure contract function and return its decoded result."""
        contract = self.get_contract(address, abi, network)
        try:
            fn = getattr(contract.functions, function_name)
        except AttributeError as exc:
            raise BlockchainServiceError(
                f"Function '{function_name}' not found in ABI"
            ) from exc
        try:
            return fn(*(args or [])).call()
        except (Web3Exception, ValueError) as exc:
            raise NetworkUnavailableError(
                f"Read call to {function_name} failed: {exc}"
            ) from exc

    # ── Signing / writes ─────────────────────────────────────────────────

    def _get_signer_account(self):
        if not self.settings.PRIVATE_KEY:
            raise WriteNotConfiguredError(
                "No PRIVATE_KEY configured on the server; write operations "
                "(deploying or calling state-changing contract functions) "
                "are disabled. Set PRIVATE_KEY in the backend's environment "
                "to enable them - see blockchain/.env.example."
            )
        w3 = self.get_web3()
        return w3.eth.account.from_key(self.settings.PRIVATE_KEY)

    def send_contract_transaction(
        self,
        address: str,
        abi: List[dict],
        function_name: str,
        args: Optional[list] = None,
        network: Optional[str] = None,
        value_wei: int = 0,
    ) -> Dict[str, Any]:
        """Sign and send a state-changing contract call using the server's
        configured signer key, and wait for the receipt.

        Raises WriteNotConfiguredError if no signer key is configured, and
        BlockchainServiceError (wrapping the revert reason where available)
        if the transaction fails.
        """
        account = self._get_signer_account()
        w3 = self.get_web3(network)
        contract = self.get_contract(address, abi, network)

        try:
            fn = getattr(contract.functions, function_name)
        except AttributeError as exc:
            raise BlockchainServiceError(
                f"Function '{function_name}' not found in ABI"
            ) from exc

        try:
            unsent_tx = fn(*(args or [])).build_transaction(
                {
                    "from": account.address,
                    "nonce": w3.eth.get_transaction_count(account.address),
                    "chainId": w3.eth.chain_id,
                    "value": value_wei,
                }
            )
            return self._sign_send_wait(w3, account, unsent_tx)
        except (Web3Exception, ValueError) as exc:
            raise BlockchainServiceError(f"Transaction failed: {exc}") from exc

    def deploy_contract(
        self,
        abi: List[dict],
        bytecode: str,
        constructor_args: Optional[list] = None,
        network: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deploy a new contract instance and wait for the receipt."""
        account = self._get_signer_account()
        w3 = self.get_web3(network)
        factory = w3.eth.contract(abi=abi, bytecode=bytecode)

        try:
            unsent_tx = factory.constructor(
                *(constructor_args or [])
            ).build_transaction(
                {
                    "from": account.address,
                    "nonce": w3.eth.get_transaction_count(account.address),
                    "chainId": w3.eth.chain_id,
                }
            )
            result = self._sign_send_wait(w3, account, unsent_tx)
        except (Web3Exception, ValueError) as exc:
            raise BlockchainServiceError(f"Deployment failed: {exc}") from exc

        result["contract_address"] = result.pop("contract_address_from_receipt", None)
        return result

    def _sign_send_wait(self, w3: Web3, account, unsent_tx: dict) -> Dict[str, Any]:
        try:
            unsent_tx["gas"] = w3.eth.estimate_gas(unsent_tx)
        except (Web3Exception, ValueError) as exc:
            # Surface the revert reason (if any) rather than a bare gas
            # estimation failure - this is almost always the useful part.
            raise BlockchainServiceError(f"Transaction would revert: {exc}") from exc

        signed = account.sign_transaction(unsent_tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        try:
            receipt = w3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=self.settings.BLOCKCHAIN_TX_TIMEOUT_SECONDS
            )
        except TimeExhausted as exc:
            raise BlockchainServiceError(
                f"Transaction {tx_hash.hex()} was not mined within "
                f"{self.settings.BLOCKCHAIN_TX_TIMEOUT_SECONDS}s"
            ) from exc

        return {
            "tx_hash": tx_hash.hex(),
            "status": "success" if receipt.status == 1 else "failed",
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "from_address": receipt["from"],
            "to_address": receipt.to,
            "contract_address_from_receipt": receipt.contractAddress,
        }

    def deploy_known_contract(
        self,
        contract_type: str,
        constructor_args: Optional[list] = None,
        network: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deploy a new instance of one of the five contract types this
        repo compiles (see KNOWN_CONTRACT_TYPES), using the bytecode/ABI
        bundled at deploy time - no external bytecode/ABI needed."""
        if contract_type not in KNOWN_CONTRACT_TYPES:
            raise BlockchainServiceError(
                f"Unknown contract type '{contract_type}'; expected one of "
                f"{KNOWN_CONTRACT_TYPES} or supply abi/bytecode directly."
            )
        abi = self.load_abi(contract_type)
        bytecode = self.load_bytecode(contract_type)
        if not abi or not bytecode:
            raise ContractNotDeployedError(
                f"No exported build artifact for {contract_type}; run "
                "`npm run export-abis` (or `npm run deploy`) in "
                "code/blockchain first."
            )
        result = self.deploy_contract(abi, bytecode, constructor_args, network)
        result["abi"] = abi
        return result

    # ── Domain-specific reads ────────────────────────────────────────────

    def get_eth_balance(self, address: str, network: Optional[str] = None) -> Decimal:
        w3 = self.get_web3(network)
        try:
            wei = w3.eth.get_balance(Web3.to_checksum_address(address))
        except (Web3Exception, ValueError) as exc:
            raise NetworkUnavailableError(
                f"Could not fetch ETH balance: {exc}"
            ) from exc
        return Decimal(wei) / Decimal(10**18)

    def get_erc20_balance(
        self, token_address: str, holder_address: str, network: Optional[str] = None
    ) -> Dict[str, Any]:
        w3 = self.get_web3(network)
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(token_address), abi=_ERC20_MIN_ABI
        )
        try:
            raw_balance = contract.functions.balanceOf(
                Web3.to_checksum_address(holder_address)
            ).call()
            decimals = contract.functions.decimals().call()
            symbol = contract.functions.symbol().call()
        except (Web3Exception, ValueError) as exc:
            raise NetworkUnavailableError(
                f"Could not fetch token balance: {exc}"
            ) from exc
        return {
            "symbol": symbol,
            "balance": Decimal(raw_balance) / Decimal(10**decimals),
            "raw_balance": raw_balance,
            "decimals": decimals,
        }

    def get_tokenized_asset_details(
        self, address: str, network: Optional[str] = None
    ) -> Dict[str, Any]:
        """Real on-chain read of a deployed TokenizedAsset contract."""
        abi = self.load_abi("TokenizedAsset")
        if abi is None:
            raise ContractNotDeployedError(
                "TokenizedAsset ABI not found; run `npm run export-abis` "
                "(or `npm run deploy`) in code/blockchain."
            )
        contract = self.get_contract(address, abi, network)
        try:
            details_tuple = contract.functions.getAssetDetails().call()
            total_supply_raw = contract.functions.totalSupply().call()
            token_name = contract.functions.name().call()
            token_symbol = contract.functions.symbol().call()
        except (Web3Exception, ValueError) as exc:
            raise NetworkUnavailableError(
                f"Could not read TokenizedAsset at {address}: {exc}"
            ) from exc

        details = dict(zip(_ASSET_DETAILS_FIELDS, details_tuple))
        details["contract_address"] = address
        details["token_name"] = token_name
        details["token_symbol"] = token_symbol
        details["total_supply"] = str(Decimal(total_supply_raw) / Decimal(10**18))
        return details


_service_singleton: Optional[BlockchainService] = None


def get_blockchain_service() -> BlockchainService:
    """FastAPI dependency / module-level accessor for a shared instance."""
    global _service_singleton
    if _service_singleton is None:
        _service_singleton = BlockchainService()
    return _service_singleton
