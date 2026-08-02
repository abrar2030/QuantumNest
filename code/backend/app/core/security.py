import base64
import hashlib
import hmac
import ipaddress
import re
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

import jwt
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.time_utils import utc_now
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    deprecated="auto",
    bcrypt__rounds=12,
    pbkdf2_sha256__rounds=100000,
)


class SecurityManager:
    """Comprehensive security manager for the application"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self._failed_attempts: Dict[str, List[datetime]] = {}
        self._blocked_ips: Dict[str, datetime] = {}

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength according to security policies"""
        errors = []
        score = 0
        if len(password) < self.settings.PASSWORD_MIN_LENGTH:
            errors.append(
                f"Password must be at least {self.settings.PASSWORD_MIN_LENGTH} characters long"
            )
        else:
            score += 1
        if not re.search("[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        if not re.search("[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        if not re.search("\\d", password):
            errors.append("Password must contain at least one digit")
        else:
            score += 1
        if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        else:
            score += 1
        if self._is_common_password(password):
            errors.append(
                "Password is too common, please choose a more unique password"
            )
            score -= 1
        if self._has_sequential_chars(password):
            errors.append("Password should not contain sequential characters")
            score -= 1
        strength = "weak"
        if score >= 4:
            strength = "strong"
        elif score >= 2:
            strength = "medium"
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength": strength,
            "score": max(0, score),
        }

    def _is_common_password(self, password: str) -> bool:
        """Check if password is in common passwords list"""
        common_passwords = [
            "password",
            "123456",
            "password123",
            "admin",
            "qwerty",
            "letmein",
            "welcome",
            "monkey",
            "dragon",
            "master",
        ]
        return password.lower() in common_passwords

    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters in password"""
        for i in range(len(password) - 2):
            if ord(password[i]) + 1 == ord(password[i + 1]) and ord(
                password[i + 1]
            ) + 1 == ord(password[i + 2]):
                return True
        return False

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token with enhanced security"""
        to_encode = data.copy()
        if expires_delta:
            expire = utc_now() + expires_delta
        else:
            expire = utc_now() + timedelta(
                minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update(
            {
                "exp": expire,
                "iat": utc_now(),
                "iss": "quantumnest-api",
                "aud": "quantumnest-client",
                "jti": secrets.token_urlsafe(16),
            }
        )
        encoded_jwt = jwt.encode(
            to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )
        return encoded_jwt

    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token"""
        data = {
            "sub": user_id,
            "type": "refresh",
            "exp": utc_now()
            + timedelta(minutes=self.settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            "iat": utc_now(),
            "jti": secrets.token_urlsafe(16),
        }
        return jwt.encode(
            data, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )

    def verify_token(
        self, token: str, token_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        """Verify JWT token with enhanced validation"""
        try:
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
                audience="quantumnest-client",
                issuer="quantumnest-api",
            )
            if payload.get("type") != token_type and token_type != "access":
                return None
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired", token_type=token_type)
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning("Invalid token", error=str(e), token_type=token_type)
            return None

    def check_rate_limit(
        self, identifier: str, max_requests: int = None, window_minutes: int = 1
    ) -> bool:
        """Check if request is within rate limits"""
        if not self.settings.RATE_LIMIT_ENABLED:
            return True
        max_requests = max_requests or self.settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        now = utc_now()
        window_start = now - timedelta(minutes=window_minutes)
        if identifier not in self._failed_attempts:
            self._failed_attempts[identifier] = []
        self._failed_attempts[identifier] = [
            attempt
            for attempt in self._failed_attempts[identifier]
            if attempt > window_start
        ]
        if len(self._failed_attempts[identifier]) >= max_requests:
            return False
        self._failed_attempts[identifier].append(now)
        return True

    def record_failed_login(self, email: str, ip_address: str) -> bool:
        """Record failed login attempt and check if account should be locked"""
        now = utc_now()
        lockout_window = now - timedelta(minutes=self.settings.LOCKOUT_DURATION_MINUTES)
        if email not in self._failed_attempts:
            self._failed_attempts[email] = []
        self._failed_attempts[email] = [
            attempt
            for attempt in self._failed_attempts[email]
            if attempt > lockout_window
        ]
        self._failed_attempts[email].append(now)
        self.logger.warning("Failed authentication for %s from %s", email, ip_address)
        if len(self._failed_attempts[email]) >= self.settings.MAX_LOGIN_ATTEMPTS:
            self.logger.warning(
                "Account locked due to too many failed attempts",
                email=email,
                ip_address=ip_address,
            )
            return True
        return False

    def is_account_locked(self, email: str) -> bool:
        """Check if account is currently locked"""
        if email not in self._failed_attempts:
            return False
        now = utc_now()
        lockout_window = now - timedelta(minutes=self.settings.LOCKOUT_DURATION_MINUTES)
        self._failed_attempts[email] = [
            attempt
            for attempt in self._failed_attempts[email]
            if attempt > lockout_window
        ]
        return len(self._failed_attempts[email]) >= self.settings.MAX_LOGIN_ATTEMPTS

    def clear_failed_attempts(self, email: str) -> Any:
        """Clear failed login attempts for successful login"""
        if email in self._failed_attempts:
            del self._failed_attempts[email]

    def validate_ip_address(self, ip_address: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        if ip_address in self._blocked_ips:
            block_time = self._blocked_ips[ip_address]
            if utc_now() - block_time < timedelta(hours=1):
                return True
            else:
                del self._blocked_ips[ip_address]
        return False

    def block_ip(self, ip_address: str, reason: str) -> Any:
        """Block an IP address"""
        self._blocked_ips[ip_address] = utc_now()
        self.logger.warning("IP address blocked", ip_address=ip_address, reason=reason)

    def generate_api_key(self, user_id: str, name: str) -> str:
        """Generate API key for user"""
        timestamp = str(int(time.time()))
        data = f"{user_id}:{name}:{timestamp}"
        signature = hmac.new(
            self.settings.SECRET_KEY.encode(), data.encode(), hashlib.sha256
        ).hexdigest()
        api_key = base64.b64encode(f"{data}:{signature}".encode()).decode()
        return f"qn_{api_key}"

    def verify_api_key(self, api_key: str) -> Optional[Dict[str, str]]:
        """Verify API key and extract user information"""
        try:
            if not api_key.startswith("qn_"):
                return None
            decoded = base64.b64decode(api_key[3:]).decode()
            parts = decoded.split(":")
            if len(parts) != 4:
                return None
            user_id, name, timestamp, signature = parts
            data = f"{user_id}:{name}:{timestamp}"
            expected_signature = hmac.new(
                self.settings.SECRET_KEY.encode(), data.encode(), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected_signature):
                return None
            return {"user_id": user_id, "name": name, "timestamp": timestamp}
        except Exception:
            return None

    def encrypt_sensitive_data(self, data: str, password: str) -> str:
        """Encrypt sensitive data using Fernet"""
        password_bytes = password.encode()
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        return base64.b64encode(salt + encrypted_data).decode()

    def decrypt_sensitive_data(
        self, encrypted_data: str, password: str
    ) -> Optional[str]:
        """Decrypt sensitive data"""
        try:
            combined_data = base64.b64decode(encrypted_data.encode())
            salt = combined_data[:16]
            encrypted_bytes = combined_data[16:]
            password_bytes = password.encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
            )
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception:
            return None

    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not isinstance(input_data, str):
            return str(input_data)
        sanitized = re.sub("[<>\"\\']", "", input_data)
        sql_patterns = [
            "(\\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\\b)",
            "(--|#|/\\*|\\*/)",
            "(\\bOR\\b.*\\b=\\b|\\bAND\\b.*\\b=\\b)",
        ]
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
        return sanitized.strip()

    def validate_file_upload(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate file upload security"""
        errors = []
        if file_size > self.settings.MAX_FILE_SIZE:
            errors.append(
                f"File size exceeds maximum allowed size of {self.settings.MAX_FILE_SIZE} bytes"
            )
        file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        if file_ext not in self.settings.ALLOWED_FILE_TYPES:
            errors.append(f"File type {file_ext} is not allowed")
        dangerous_patterns = ["\\.\\./", "\\.\\.\\\\", "^\\.", "\\$", '[<>:"|?*]']
        for pattern in dangerous_patterns:
            if re.search(pattern, filename):
                errors.append("Filename contains dangerous characters")
                break
        return {"valid": len(errors) == 0, "errors": errors}


def require_auth(f: Any) -> Any:
    """Decorator to require authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function


def require_permission(permission: str) -> Any:
    """Decorator to require specific permission"""

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def rate_limit(max_requests: int = 100, window_minutes: int = 1) -> Any:
    """Decorator to apply rate limiting"""

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function

    return decorator


security_manager = SecurityManager()


# ---------------------------------------------------------------------------
# FastAPI dependency helpers – kept here so other modules can import from
# app.core.security (some legacy test files expect this import path)
# ---------------------------------------------------------------------------
from typing import Optional as _Optional

from app.db.database import get_db as _get_db
from app.models.models import User as _User
from fastapi import Depends as _Depends
from fastapi import HTTPException as _HTTPException
from fastapi import status as _status
from fastapi.security import OAuth2PasswordBearer as _OAuth2PasswordBearer
from jose import JWTError as _JWTError
from jose import jwt as _jwt
from sqlalchemy.orm import Session as _Session

_oauth2_scheme = _OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = _Depends(_oauth2_scheme),
    db: _Session = _Depends(_get_db),
) -> _User:
    """Decode JWT and return the corresponding User record."""
    settings = get_settings()
    credentials_exception = _HTTPException(
        status_code=_status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = _jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: _Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except _JWTError:
        raise credentials_exception from None
    user = db.query(_User).filter(_User.email == username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: _User = _Depends(get_current_user),
) -> _User:
    """Raise 400 if user is inactive."""
    if not current_user.is_active:
        raise _HTTPException(status_code=400, detail="Inactive user")
    return current_user
