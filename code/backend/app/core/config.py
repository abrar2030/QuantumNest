import secrets
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # ── App ──────────────────────────────────────────────────────────────────
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    PROJECT_NAME: str = "QuantumNest Capital API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Advanced Financial Platform with AI-Powered Analytics"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = secrets.token_hex(32)
    API_SECRET_KEY: str = secrets.token_hex(32)
    API_KEY: str = "default-api-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./quantumnest.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["*"]

    # ── Rate limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 200

    # ── Feature flags ─────────────────────────────────────────────────────────
    ENABLE_REQUEST_SIGNING: bool = False
    ENABLE_IP_FILTERING: bool = False
    ENABLE_CSRF_PROTECTION: bool = True
    ENABLE_REGISTRATION: bool = True
    ENABLE_EMAIL_VERIFICATION: bool = False
    ENABLE_TWO_FACTOR_AUTH: bool = False
    ENABLE_ADVANCED_ANALYTICS: bool = True
    ENABLE_REAL_TIME_UPDATES: bool = True

    # ── AI / ML ───────────────────────────────────────────────────────────────
    AI_MODELS_DIR: str = "./models"
    AI_MODEL_CACHE_SIZE: int = 5
    AI_PREDICTION_TIMEOUT: int = 30
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    YAHOO_FINANCE_ENABLED: bool = True
    QUANDL_API_KEY: Optional[str] = None
    IEX_CLOUD_API_KEY: Optional[str] = None

    # ── Blockchain ────────────────────────────────────────────────────────────
    ETHEREUM_RPC_URL: str = "http://localhost:8545"
    POLYGON_RPC_URL: str = "https://polygon-rpc.com"
    BSC_RPC_URL: str = "https://bsc-dataseed.binance.org"
    PRIVATE_KEY: Optional[str] = None
    CONTRACT_ADDRESSES: Dict[str, str] = {}
    # Which network's deployment (see blockchain/deployments/<name>.json) to
    # load contract addresses + ABIs from. Must match a file written by
    # `npm run deploy -- --network <BLOCKCHAIN_NETWORK>` in code/blockchain.
    BLOCKCHAIN_NETWORK: str = "localhost"
    # Where to find blockchain/deployments/. Defaults to the sibling
    # directory that exists when backend/ and blockchain/ are checked out
    # side-by-side under code/ (the common local-dev layout); in Docker
    # this is overridden to the shared volume mount (see docker-compose.yml).
    BLOCKCHAIN_DEPLOYMENTS_DIR: str = "../blockchain/deployments"
    # Wei to allow as gas price headroom multiplier isn't configurable here;
    # keep write operations opt-in and explicit instead: if PRIVATE_KEY is
    # unset, blockchain endpoints that would send a transaction return a
    # clear 503 rather than silently pretending to succeed.
    BLOCKCHAIN_TX_TIMEOUT_SECONDS: int = 120

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    LOG_MAX_SIZE: int = 10 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 5

    # ── Monitoring ────────────────────────────────────────────────────────────
    METRICS_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL: int = 30
    PROMETHEUS_ENABLED: bool = False
    SENTRY_DSN: Optional[str] = None

    # ── Email ─────────────────────────────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    EMAIL_FROM: Optional[str] = None

    # ── File storage ──────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".csv", ".xlsx", ".json"]

    # ── Misc ──────────────────────────────────────────────────────────────────
    CACHE_TTL: int = 300
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: Any) -> Any:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("PASSWORD_MIN_LENGTH")
    @classmethod
    def validate_password_length(cls, v: Any) -> Any:
        if v < 8:
            raise ValueError("PASSWORD_MIN_LENGTH must be at least 8")
        return v

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @model_validator(mode="after")
    def warn_insecure_production(self) -> "Settings":
        if self.ENVIRONMENT == Environment.PRODUCTION:
            if self.SECRET_KEY == secrets.token_hex(32):
                raise ValueError("SECRET_KEY must be explicitly set in production")
            if "*" in self.ALLOWED_ORIGINS:
                import warnings

                warnings.warn(
                    "ALLOWED_ORIGINS='*' in production is insecure", stacklevel=2
                )
        return self

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "use_enum_values": True,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


def get_database_url(settings: Optional[Settings] = None) -> str:
    """Return the database URL for the current environment."""
    s = settings or get_settings()
    return s.DATABASE_URL


def is_production() -> bool:
    return get_settings().ENVIRONMENT == Environment.PRODUCTION


def is_development() -> bool:
    return get_settings().ENVIRONMENT == Environment.DEVELOPMENT
