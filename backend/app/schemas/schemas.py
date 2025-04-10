from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# User schemas
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserTier(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER
    tier: Optional[UserTier] = UserTier.BASIC

class User(UserBase):
    id: int
    role: UserRole
    tier: UserTier
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Portfolio schemas
class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Asset schemas
class AssetBase(BaseModel):
    symbol: str
    name: str
    asset_type: str
    description: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Portfolio Asset schemas
class PortfolioAssetBase(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: float
    purchase_price: float
    purchase_date: datetime

class PortfolioAssetCreate(PortfolioAssetBase):
    pass

class PortfolioAsset(PortfolioAssetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Asset Price schemas
class AssetPriceBase(BaseModel):
    asset_id: int
    price: float

class AssetPriceCreate(AssetPriceBase):
    pass

class AssetPrice(AssetPriceBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# Transaction schemas
class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class TransactionBase(BaseModel):
    user_id: int
    asset_id: Optional[int] = None
    transaction_type: TransactionType
    amount: float
    quantity: Optional[float] = None
    price: Optional[float] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    status: TransactionStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# AI Model schemas
class AIModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_type: str
    accuracy: float

class AIModelCreate(AIModelBase):
    pass

class AIModel(AIModelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# AI Prediction schemas
class AIPredictionBase(BaseModel):
    model_id: int
    asset_id: Optional[int] = None
    prediction_type: str
    prediction_value: float
    confidence: float
    target_date: datetime

class AIPredictionCreate(AIPredictionBase):
    pass

class AIPrediction(AIPredictionBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# Smart Contract schemas
class SmartContractBase(BaseModel):
    address: str
    name: str
    contract_type: str
    abi: str
    bytecode: str
    network: str

class SmartContractCreate(SmartContractBase):
    pass

class SmartContract(SmartContractBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Blockchain Transaction schemas
class BlockchainTransactionBase(BaseModel):
    tx_hash: str
    from_address: str
    to_address: str
    contract_id: Optional[int] = None
    value: float
    gas_used: int
    status: str

class BlockchainTransactionCreate(BlockchainTransactionBase):
    pass

class BlockchainTransaction(BlockchainTransactionBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# System Log schemas
class SystemLogBase(BaseModel):
    log_level: str
    component: str
    message: str

class SystemLogCreate(SystemLogBase):
    pass

class SystemLog(SystemLogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# Portfolio with assets
class PortfolioWithAssets(Portfolio):
    assets: List[PortfolioAsset] = []

# User with portfolios
class UserWithPortfolios(User):
    portfolios: List[Portfolio] = []
