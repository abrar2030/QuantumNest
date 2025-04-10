from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class UserTier(str, enum.Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    tier = Column(Enum(UserTier), default=UserTier.BASIC)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    portfolios = relationship("Portfolio", back_populates="owner")
    transactions = relationship("Transaction", back_populates="user")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="portfolios")
    assets = relationship("PortfolioAsset", back_populates="portfolio")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    asset_type = Column(String)  # stock, bond, crypto, etc.
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    portfolio_assets = relationship("PortfolioAsset", back_populates="asset")
    price_history = relationship("AssetPrice", back_populates="asset")

class PortfolioAsset(Base):
    __tablename__ = "portfolio_assets"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    quantity = Column(Float)
    purchase_price = Column(Float)
    purchase_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    portfolio = relationship("Portfolio", back_populates="assets")
    asset = relationship("Asset", back_populates="portfolio_assets")

class AssetPrice(Base):
    __tablename__ = "asset_prices"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    price = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    asset = relationship("Asset", back_populates="price_history")

class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    transaction_type = Column(Enum(TransactionType))
    amount = Column(Float)
    quantity = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="transactions")
    asset = relationship("Asset")

class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    model_type = Column(String)  # LSTM, GARCH, PCA, etc.
    accuracy = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    predictions = relationship("AIPrediction", back_populates="model")

class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    prediction_type = Column(String)  # price, trend, risk, etc.
    prediction_value = Column(Float)
    confidence = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    target_date = Column(DateTime(timezone=True))

    model = relationship("AIModel", back_populates="predictions")
    asset = relationship("Asset")

class SmartContract(Base):
    __tablename__ = "smart_contracts"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    name = Column(String)
    contract_type = Column(String)  # trading, token, management, etc.
    abi = Column(Text)
    bytecode = Column(Text)
    network = Column(String)  # mainnet, testnet, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    transactions = relationship("BlockchainTransaction", back_populates="contract")

class BlockchainTransaction(Base):
    __tablename__ = "blockchain_transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String, unique=True, index=True)
    from_address = Column(String)
    to_address = Column(String)
    contract_id = Column(Integer, ForeignKey("smart_contracts.id"), nullable=True)
    value = Column(Float)
    gas_used = Column(Integer)
    status = Column(String)  # confirmed, pending, failed
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    contract = relationship("SmartContract", back_populates="transactions")

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_level = Column(String)  # info, warning, error, critical
    component = Column(String)  # api, database, blockchain, ai, etc.
    message = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
