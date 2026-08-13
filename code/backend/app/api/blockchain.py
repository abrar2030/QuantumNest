from typing import Any, List, Optional

from app.core.config import get_settings
from app.core.time_utils import utc_now
from app.db.database import get_db
from app.main import get_current_active_user
from app.models import models
from app.schemas import schemas
from app.services.blockchain_service import (
    KNOWN_CONTRACT_TYPES,
    BlockchainServiceError,
    ContractNotDeployedError,
    NetworkUnavailableError,
    WriteNotConfiguredError,
    get_blockchain_service,
    is_read_only_function,
    json_safe,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


def _raise_for_service_error(exc: BlockchainServiceError) -> None:
    """Map a BlockchainService exception onto the right HTTP status."""
    if isinstance(exc, WriteNotConfiguredError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )
    if isinstance(exc, ContractNotDeployedError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, NetworkUnavailableError):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


def _enrich_tokenized_asset(details: dict) -> dict:
    """Add frontend-friendly aliases derived from real on-chain fields.

    `asset_value` is the contract's own reported valuation (in USD cents,
    set by its owner via TokenizedAsset.updateAssetValue) - not a live
    market price from an oracle, but a real on-chain number, so deriving
    a dollar "price per token" and a market cap from it is a straight unit
    conversion, not fabrication. No externally-sourced price data is
    involved anywhere here.
    """
    enriched = dict(details)
    price_per_token = details.get("asset_value", 0) / 100
    total_supply = float(details.get("total_supply", 0) or 0)
    enriched["name"] = details.get("token_name")
    enriched["underlying_asset"] = details.get("asset_name")
    enriched["price_per_token"] = price_per_token
    enriched["market_cap"] = price_per_token * total_supply
    return enriched


@router.get("/contracts/", response_model=List[schemas.SmartContract])
def get_smart_contracts(
    skip: int = 0,
    limit: int = 100,
    contract_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    query = db.query(models.SmartContract).filter(
        models.SmartContract.is_active == True
    )
    if contract_type:
        query = query.filter(models.SmartContract.contract_type == contract_type)
    contracts = query.offset(skip).limit(limit).all()
    return contracts


@router.post(
    "/contracts/",
    response_model=schemas.SmartContract,
    status_code=status.HTTP_201_CREATED,
)
def create_smart_contract(
    contract: schemas.SmartContractCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    existing = (
        db.query(models.SmartContract)
        .filter(models.SmartContract.address == contract.address)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409, detail="Contract with this address already exists"
        )
    db_contract = models.SmartContract(
        address=contract.address,
        name=contract.name,
        contract_type=contract.contract_type,
        network=contract.network,
        abi=contract.abi,
        bytecode=contract.bytecode,
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@router.get("/contracts/{contract_id}", response_model=schemas.SmartContract)
def get_smart_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    db_contract = (
        db.query(models.SmartContract)
        .filter(models.SmartContract.id == contract_id)
        .first()
    )
    if db_contract is None:
        raise HTTPException(status_code=404, detail="Smart contract not found")
    return db_contract


@router.get("/transactions/", response_model=List[schemas.BlockchainTransaction])
def get_blockchain_transactions(
    skip: int = 0,
    limit: int = 100,
    contract_id: Optional[int] = None,
    network: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    query = db.query(models.BlockchainTransaction)
    if contract_id:
        query = query.filter(models.BlockchainTransaction.contract_id == contract_id)
    if network:
        query = query.filter(models.BlockchainTransaction.network == network)
    transactions = (
        query.order_by(models.BlockchainTransaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions


@router.get("/transactions/{tx_hash}", response_model=schemas.BlockchainTransaction)
def get_blockchain_transaction(
    tx_hash: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    db_transaction = (
        db.query(models.BlockchainTransaction)
        .filter(models.BlockchainTransaction.tx_hash == tx_hash)
        .first()
    )
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Blockchain transaction not found")
    return db_transaction


@router.get("/wallet/{address}/balance")
def get_wallet_balance(
    address: str,
    network: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """Real ETH balance (and, where deployed, the demo QNT token balance)
    for `address` on `network`, read live from the chain. No price feed is
    wired up, so no USD conversion is included - only real observed
    balances.
    """
    if not address.startswith("0x") or len(address) != 42:
        raise HTTPException(status_code=400, detail="Invalid Ethereum wallet address")

    settings = get_settings()
    network = network or settings.BLOCKCHAIN_NETWORK
    service = get_blockchain_service()

    if not service.is_connected(network):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not reach an RPC endpoint for network '{network}'",
        )

    try:
        eth_balance = service.get_eth_balance(address, network)
    except BlockchainServiceError as exc:
        _raise_for_service_error(exc)

    balances = {"ETH": {"balance": str(eth_balance)}}

    test_token_address = service.get_known_contract_address("TestToken", network)
    if test_token_address:
        try:
            token_balance = service.get_erc20_balance(
                test_token_address, address, network
            )
            balances[token_balance["symbol"]] = {
                "balance": str(token_balance["balance"]),
                "contract_address": test_token_address,
            }
        except BlockchainServiceError:
            # Token balance is a bonus, not required for the endpoint to
            # succeed - the ETH balance above already answered the question.
            pass

    return {
        "address": address,
        "network": network,
        "balances": balances,
        "timestamp": utc_now().isoformat(),
    }


@router.post("/deploy/contract")
def deploy_smart_contract(
    contract_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """Deploy a real contract instance on-chain.

    `contract_data` must include either:
      - `contract_type`: one of KNOWN_CONTRACT_TYPES, to deploy a fresh
        instance using this repo's own compiled bytecode/ABI, or
      - `abi` and `bytecode`: to deploy an arbitrary externally-compiled
        contract.
    Optional: `name` (display name), `network` (defaults to the server's
    configured network), `constructor_args` (positional list).

    Requires the server to have PRIVATE_KEY configured (503 otherwise).
    """
    allowed_tiers = ["premium", "professional", "enterprise", "institutional"]
    user_tier = (
        current_user.tier.value
        if hasattr(current_user.tier, "value")
        else str(current_user.tier)
    )
    if user_tier not in allowed_tiers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Smart contract deployment requires Premium tier or higher",
        )

    settings = get_settings()
    network = contract_data.get("network") or settings.BLOCKCHAIN_NETWORK
    contract_type = contract_data.get("contract_type")
    abi = contract_data.get("abi")
    bytecode = contract_data.get("bytecode")
    constructor_args = contract_data.get("constructor_args", [])
    name = contract_data.get("name") or contract_type or "Unnamed Contract"

    service = get_blockchain_service()

    try:
        if abi and bytecode:
            deploy_result = service.deploy_contract(
                abi, bytecode, constructor_args, network
            )
            deploy_result["abi"] = abi
        elif contract_type:
            deploy_result = service.deploy_known_contract(
                contract_type, constructor_args, network
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Provide either 'contract_type' (one of "
                    f"{KNOWN_CONTRACT_TYPES}) or both 'abi' and 'bytecode'."
                ),
            )
    except BlockchainServiceError as exc:
        _raise_for_service_error(exc)

    if deploy_result["status"] != "success":
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Deployment transaction reverted: {deploy_result['tx_hash']}",
        )

    w3 = service.get_web3(network)
    db_contract = models.SmartContract(
        address=deploy_result["contract_address"],
        name=name,
        contract_type=contract_type or "custom",
        network=network,
        chain_id=w3.eth.chain_id,
        abi=deploy_result["abi"],
        bytecode=bytecode or service.load_bytecode(contract_type),
        deployment_tx_hash=deploy_result["tx_hash"],
        is_verified=bool(contract_type),  # bundled source == verified
        is_active=True,
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    db_transaction = models.BlockchainTransaction(
        tx_hash=deploy_result["tx_hash"],
        contract_id=db_contract.id,
        from_address=deploy_result["from_address"],
        to_address=deploy_result["contract_address"],
        value=0,
        gas_used=deploy_result["gas_used"],
        block_number=deploy_result["block_number"],
        status=deploy_result["status"],
        network=network,
    )
    db.add(db_transaction)
    db.commit()

    return {
        "status": deploy_result["status"],
        "contract_id": db_contract.id,
        "contract_name": name,
        "contract_type": db_contract.contract_type,
        "address": deploy_result["contract_address"],
        "transaction_hash": deploy_result["tx_hash"],
        "block_number": deploy_result["block_number"],
        "gas_used": deploy_result["gas_used"],
        "timestamp": utc_now().isoformat(),
        "network": network,
    }


@router.post("/execute/contract/{contract_id}")
def execute_smart_contract(
    contract_id: int,
    function_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """Call a real function on a previously deployed/registered contract.

    `function_data`: {"function": "<name>", "args": [...]}. Whether this
    is a free read (`.call()`) or a signed transaction is determined
    automatically from the contract's own ABI (view/pure vs
    nonpayable/payable) - state-changing calls require PRIVATE_KEY to be
    configured on the server (503 otherwise).
    """
    db_contract = (
        db.query(models.SmartContract)
        .filter(
            models.SmartContract.id == contract_id,
            models.SmartContract.is_active == True,
        )
        .first()
    )
    if db_contract is None:
        raise HTTPException(status_code=404, detail="Smart contract not found")
    if not db_contract.abi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This contract has no ABI on record; cannot determine its "
            "functions. Re-register it with an ABI via POST /contracts/.",
        )

    function_name = function_data.get("function")
    if not function_name:
        raise HTTPException(status_code=400, detail="'function' is required")
    args = function_data.get("args", [])
    network = function_data.get("network") or db_contract.network

    service = get_blockchain_service()

    try:
        if is_read_only_function(db_contract.abi, function_name):
            result = service.call_read_function(
                db_contract.address, db_contract.abi, function_name, args, network
            )
            return {
                "status": "success",
                "contract_id": contract_id,
                "contract_address": db_contract.address,
                "function_name": function_name,
                "result": json_safe(result),
                "timestamp": utc_now().isoformat(),
            }

        tx_result = service.send_contract_transaction(
            db_contract.address, db_contract.abi, function_name, args, network
        )
    except BlockchainServiceError as exc:
        _raise_for_service_error(exc)

    db_transaction = models.BlockchainTransaction(
        tx_hash=tx_result["tx_hash"],
        contract_id=db_contract.id,
        from_address=tx_result["from_address"],
        to_address=db_contract.address,
        value=0,
        gas_used=tx_result["gas_used"],
        block_number=tx_result["block_number"],
        status=tx_result["status"],
        network=network,
    )
    db.add(db_transaction)
    db.commit()

    return {
        "status": tx_result["status"],
        "contract_id": contract_id,
        "contract_address": db_contract.address,
        "function_name": function_name,
        "transaction_hash": tx_result["tx_hash"],
        "block_number": tx_result["block_number"],
        "gas_used": tx_result["gas_used"],
        "timestamp": utc_now().isoformat(),
    }


@router.get("/tokenization/assets")
def get_tokenized_assets(
    skip: int = 0,
    limit: int = 100,
    network: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """Real on-chain details (via TokenizedAsset.getAssetDetails()) for
    every active TokenizedAsset-type contract on record, enriched with a
    few presentation-friendly aliases derived from those same on-chain
    fields (see _enrich_tokenized_asset) - no externally-sourced price
    data. Contracts get on record either by being deployed through
    POST /deploy/contract, by being registered through POST /contracts/,
    or - for the network this server is configured for - automatically,
    from the chain's own deployment manifest
    (blockchain/deployments/<network>.json), so a freshly `npm run
    deploy`-ed local chain shows up here with no manual registration step.
    """
    settings = get_settings()
    network = network or settings.BLOCKCHAIN_NETWORK
    service = get_blockchain_service()

    db_contracts = (
        db.query(models.SmartContract)
        .filter(
            models.SmartContract.contract_type == "TokenizedAsset",
            models.SmartContract.is_active == True,
            models.SmartContract.network == network,
        )
        .all()
    )
    addresses = [c.address for c in db_contracts]

    if not addresses:
        known_address = service.get_known_contract_address("TokenizedAsset", network)
        if known_address:
            addresses = [known_address]

    assets = []
    errors = []
    for address in addresses[skip : skip + limit]:
        try:
            details = service.get_tokenized_asset_details(address, network)
            assets.append(_enrich_tokenized_asset(details))
        except BlockchainServiceError as exc:
            errors.append({"contract_address": address, "error": str(exc)})

    return {
        "total": len(addresses),
        "network": network,
        "data": assets,
        "errors": errors or None,
    }


@router.get("/networks")
def get_supported_networks(
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """Live status (reachable? contracts deployed?) for every network this
    server knows an RPC endpoint for - not a static, possibly-stale list.
    """
    service = get_blockchain_service()

    candidates = [
        {
            "id": "localhost",
            "name": "Local Hardhat Node",
            "chain_id": 31337,
            "currency": "ETH",
        },
        {
            "id": "sepolia",
            "name": "Ethereum Sepolia Testnet",
            "chain_id": 11155111,
            "currency": "ETH",
        },
        {
            "id": "polygon_amoy",
            "name": "Polygon Amoy Testnet",
            "chain_id": 80002,
            "currency": "MATIC",
        },
        {
            "id": "polygon",
            "name": "Polygon Mainnet",
            "chain_id": 137,
            "currency": "MATIC",
        },
        {"id": "bsc", "name": "BNB Smart Chain", "chain_id": 56, "currency": "BNB"},
    ]

    networks = []
    for candidate in candidates:
        connected = service.is_connected(candidate["id"])
        networks.append(
            {
                **candidate,
                "reachable": connected,
                "contracts_deployed": bool(service.known_contracts(candidate["id"])),
            }
        )

    return {"default_network": get_settings().BLOCKCHAIN_NETWORK, "networks": networks}
