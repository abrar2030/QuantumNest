from typing import Any, List, Optional

from app.core.time_utils import utc_now
from app.db.database import get_db
from app.main import get_current_active_user
from app.models import models
from app.schemas import schemas
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


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
    network: str = "ethereum",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    if not address.startswith("0x") or len(address) != 42:
        raise HTTPException(status_code=400, detail="Invalid Ethereum wallet address")
    return {
        "address": address,
        "network": network,
        "balances": {
            "ETH": {"balance": 1.245, "value_usd": 3981.60},
            "USDC": {"balance": 5000.0, "value_usd": 5000.0},
            "USDT": {"balance": 2500.0, "value_usd": 2500.0},
        },
        "total_value_usd": 11481.60,
        "timestamp": utc_now().isoformat(),
    }


@router.post("/deploy/contract")
def deploy_smart_contract(
    contract_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    allowed_tiers = ["premium", "professional", "enterprise", "institutional"]
    if str(current_user.tier) not in allowed_tiers and not any(
        t in str(current_user.tier) for t in allowed_tiers
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Smart contract deployment requires Premium tier or higher",
        )
    return {
        "status": "success",
        "contract_name": contract_data.get("name", "Unnamed Contract"),
        "contract_type": contract_data.get("type", "Unknown"),
        "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "transaction_hash": "0x7d2a5b3e8f4a1b9c6d8e7f0a2b3c4d5e6f7a8b9c",
        "block_number": 19250050,
        "gas_used": 1250000,
        "timestamp": utc_now().isoformat(),
        "network": contract_data.get("network", "Ethereum Testnet"),
    }


@router.post("/execute/contract/{contract_id}")
def execute_smart_contract(
    contract_id: int,
    function_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
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
    return {
        "status": "success",
        "contract_id": contract_id,
        "contract_address": db_contract.address,
        "function_name": function_data.get("function", "unknown"),
        "transaction_hash": "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b",
        "block_number": 19250055,
        "gas_used": 75000,
        "timestamp": utc_now().isoformat(),
        "result": "Function executed successfully",
    }


@router.get("/tokenization/assets")
def get_tokenized_assets(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    tokenized_assets = [
        {
            "token_symbol": "QNC-AAPL",
            "name": "Tokenized Apple Inc.",
            "contract_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "total_supply": 10000,
            "price_per_token": 2.15,
            "underlying_asset": "AAPL",
            "market_cap": 21500.0,
        },
        {
            "token_symbol": "QNC-TSLA",
            "name": "Tokenized Tesla Inc.",
            "contract_address": "0x8901DaECbfF9e1d2c7b9C2a154b9dAc45a1B5092",
            "total_supply": 5000,
            "price_per_token": 1.8,
            "underlying_asset": "TSLA",
            "market_cap": 9000.0,
        },
        {
            "token_symbol": "QNC-GOLD",
            "name": "Tokenized Gold",
            "contract_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
            "total_supply": 20000,
            "price_per_token": 0.95,
            "underlying_asset": "Gold",
            "market_cap": 19000.0,
        },
        {
            "token_symbol": "QNC-REITS",
            "name": "Tokenized Real Estate Index",
            "contract_address": "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
            "total_supply": 15000,
            "price_per_token": 1.25,
            "underlying_asset": "Real Estate Index",
            "market_cap": 18750.0,
        },
    ]
    return {
        "total": len(tokenized_assets),
        "data": tokenized_assets[skip : skip + limit],
    }


@router.get("/networks")
def get_supported_networks(
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    return {
        "networks": [
            {
                "id": "ethereum",
                "name": "Ethereum Mainnet",
                "chain_id": 1,
                "currency": "ETH",
            },
            {"id": "polygon", "name": "Polygon", "chain_id": 137, "currency": "MATIC"},
            {"id": "bsc", "name": "BNB Smart Chain", "chain_id": 56, "currency": "BNB"},
            {
                "id": "arbitrum",
                "name": "Arbitrum One",
                "chain_id": 42161,
                "currency": "ETH",
            },
            {
                "id": "goerli",
                "name": "Goerli Testnet",
                "chain_id": 5,
                "currency": "ETH",
            },
        ]
    }
