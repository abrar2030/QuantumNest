from datetime import timedelta
from typing import Any
from unittest.mock import Mock, patch

import bcrypt
import jwt
import pyotp
import pytest
from app.auth.authentication import (
    AdvancedAuthenticationSystem,
    SessionInfo,
    SessionStatus,
)
from app.core.time_utils import utc_now
from app.models.models import LoginAttempt, UserSession


class TestAdvancedAuthenticationSystem:
    """Test cases for AdvancedAuthenticationSystem"""

    def test_init(self, db_session: Any, mock_redis: Any) -> Any:
        """Test authentication system initialization"""
        with patch("app.auth.authentication.redis.Redis", return_value=mock_redis):
            auth_system = AdvancedAuthenticationSystem(db_session)
            assert auth_system.db == db_session
            assert auth_system.redis_client == mock_redis
            assert auth_system.jwt_secret is not None
            assert auth_system.max_login_attempts == 5

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_system, db_session, test_user):
        """Test successful user authentication"""
        password = "TestPassword123!"
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        test_user.hashed_password = hashed_password
        db_session.commit()
        auth_system._check_rate_limit = Mock(return_value=True)
        auth_system._is_account_locked = Mock(return_value=False)
        auth_system._calculate_authentication_risk = Mock(return_value=0.3)
        auth_system._create_session = Mock(
            return_value=SessionInfo(
                session_id="test_session",
                user_id=str(test_user.id),
                device_fingerprint="test_device",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                created_at=utc_now(),
                last_activity=utc_now(),
                expires_at=utc_now() + timedelta(hours=24),
                status=SessionStatus.ACTIVE,
                risk_score=0.3,
                location=None,
            )
        )
        result = await auth_system.authenticate_user(
            email=test_user.email,
            password=password,
            device_fingerprint="test_device",
            ip_address="127.0.0.1",
            user_agent="test_agent",
        )
        assert result.success is True
        assert result.user_id == str(test_user.id)
        assert result.session_token == "test_session"
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.requires_2fa is False

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email(self, auth_system):
        """Test authentication with invalid email"""
        result = await auth_system.authenticate_user(
            email="nonexistent@example.com",
            password="password",
            device_fingerprint="test_device",
            ip_address="127.0.0.1",
            user_agent="test_agent",
        )
        assert result.success is False
        assert result.error_message == "Invalid credentials"
        assert result.risk_score == 0.8

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(
        self, auth_system, db_session, test_user
    ):
        """Test authentication with invalid password"""
        hashed_password = bcrypt.hashpw(b"correct_password", bcrypt.gensalt()).decode(
            "utf-8"
        )
        test_user.hashed_password = hashed_password
        db_session.commit()
        auth_system._check_rate_limit = Mock(return_value=True)
        auth_system._is_account_locked = Mock(return_value=False)
        auth_system._log_login_attempt = Mock()
        auth_system._increment_failed_attempts = Mock()
        result = await auth_system.authenticate_user(
            email=test_user.email,
            password="wrong_password",
            device_fingerprint="test_device",
            ip_address="127.0.0.1",
            user_agent="test_agent",
        )
        assert result.success is False
        assert result.error_message == "Invalid credentials"
        assert result.risk_score == 0.7
        auth_system._log_login_attempt.assert_called_once()
        auth_system._increment_failed_attempts.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_rate_limited(self, auth_system, test_user):
        """Test authentication when rate limited"""
        auth_system._check_rate_limit = Mock(return_value=False)
        result = await auth_system.authenticate_user(
            email=test_user.email,
            password="password",
            device_fingerprint="test_device",
            ip_address="127.0.0.1",
            user_agent="test_agent",
        )
        assert result.success is False
        assert "Too many login attempts" in result.error_message
        assert result.risk_score == 1.0

    @pytest.mark.asyncio
    async def test_authenticate_user_account_locked(
        self, auth_system, db_session, test_user
    ):
        """Test authentication when account is locked"""
        auth_system._check_rate_limit = Mock(return_value=True)
        auth_system._is_account_locked = Mock(return_value=True)
        result = await auth_system.authenticate_user(
            email=test_user.email,
            password="password",
            device_fingerprint="test_device",
            ip_address="127.0.0.1",
            user_agent="test_agent",
        )
        assert result.success is False
        assert "Account is temporarily locked" in result.error_message
        assert result.risk_score == 1.0

    @pytest.mark.asyncio
    async def test_authenticate_user_requires_2fa(
        self, auth_system, db_session, test_user
    ):
        """Test authentication when 2FA is required"""
        test_user.two_factor_enabled = True
        test_user.two_factor_secret = pyotp.random_base32()
        db_session.commit()
        password = "TestPassword123!"
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        test_user.hashed_password = hashed_password
        db_session.commit()
        auth_system._check_rate_limit = Mock(return_value=True)
        auth_system._is_account_locked = Mock(return_value=False)
        auth_system._calculate_authentication_risk = Mock(return_value=0.3)
        auth_system._create_temp_session = Mock(return_value="temp_session_123")
        result = await auth_system.authenticate_user(
            email=test_user.email,
            password=password,
            device_fingerprint="test_device",
            ip_address="127.0.0.1",
            user_agent="test_agent",
        )
        assert result.success is False
        assert result.requires_2fa is True
        assert result.session_token == "temp_session_123"
        assert "Two-factor authentication required" in result.error_message

    @pytest.mark.asyncio
    async def test_verify_2fa_success(self, auth_system, db_session, test_user):
        """Test successful 2FA verification"""
        secret = pyotp.random_base32()
        test_user.two_factor_secret = secret
        test_user.two_factor_enabled = True
        db_session.commit()
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()
        auth_system._check_rate_limit = Mock(return_value=True)
        auth_system._verify_temp_session = Mock(return_value=True)
        auth_system._calculate_authentication_risk = Mock(return_value=0.3)
        auth_system._create_session = Mock(
            return_value=SessionInfo(
                session_id="test_session",
                user_id=str(test_user.id),
                device_fingerprint="test_device",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                created_at=utc_now(),
                last_activity=utc_now(),
                expires_at=utc_now() + timedelta(hours=24),
                status=SessionStatus.ACTIVE,
                risk_score=0.3,
                location=None,
            )
        )
        auth_system._cleanup_temp_session = Mock()
        auth_system._log_login_attempt = Mock()
        result = await auth_system.verify_2fa(
            user_id=str(test_user.id),
            temp_session="temp_session_123",
            totp_code=valid_code,
            device_fingerprint="test_device",
            ip_address="127.0.0.1",
            user_agent="test_agent",
        )
        assert result.success is True
        assert result.user_id == str(test_user.id)
        assert result.session_token == "test_session"
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.requires_2fa is False

    @pytest.mark.asyncio
    async def test_verify_2fa_invalid_code(self, auth_system, db_session, test_user):
        """Test 2FA verification with invalid code"""
        secret = pyotp.random_base32()
        test_user.two_factor_secret = secret
        test_user.two_factor_enabled = True
        db_session.commit()
        auth_system._check_rate_limit = Mock(return_value=True)
        auth_system._verify_temp_session = Mock(return_value=True)
        auth_system._log_login_attempt = Mock()
        result = await auth_system.verify_2fa(
            user_id=str(test_user.id),
            temp_session="temp_session_123",
            totp_code="000000",
            device_fingerprint="test_device",
            ip_address="127.0.0.1",
            user_agent="test_agent",
        )
        assert result.success is False
        assert result.requires_2fa is True
        assert result.error_message == "Invalid 2FA code"
        assert result.risk_score == 0.7

    def test_setup_2fa(self, auth_system: Any, test_user: Any) -> Any:
        """Test 2FA setup"""
        result = auth_system.setup_2fa(str(test_user.id))
        assert result["success"] is True
        assert "secret" in result
        assert "qr_code" in result
        assert "manual_entry_key" in result
        assert result["qr_code"].startswith("data:image/png;base64,")

    def test_confirm_2fa_setup_success(
        self, auth_system: Any, db_session: Any, test_user: Any
    ) -> Any:
        """Test successful 2FA setup confirmation"""
        secret = pyotp.random_base32()
        auth_system.redis_client.get = Mock(return_value=secret)
        auth_system.redis_client.delete = Mock()
        auth_system._generate_backup_codes = Mock(return_value=["CODE1", "CODE2"])
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()
        result = auth_system.confirm_2fa_setup(str(test_user.id), valid_code)
        assert result["success"] is True
        assert "backup_codes" in result
        db_session.refresh(test_user)
        assert test_user.two_factor_secret == secret
        assert test_user.two_factor_enabled is True

    def test_validate_token_valid(self, auth_system: Any) -> Any:
        """Test token validation with valid token"""
        user_id = "123"
        session_id = "session_123"
        auth_system._is_session_valid = Mock(return_value=True)
        auth_system._update_session_activity = Mock()
        token = auth_system._generate_access_token(user_id, session_id)
        result = auth_system.validate_token(token)
        assert result is not None
        assert result["user_id"] == user_id
        assert result["session_id"] == session_id
        assert result["type"] == "access"

    def test_validate_token_expired(self, auth_system: Any) -> Any:
        """Test token validation with expired token"""
        payload = {
            "user_id": "123",
            "session_id": "session_123",
            "type": "access",
            "exp": utc_now() - timedelta(hours=1),
            "iat": utc_now() - timedelta(hours=2),
        }
        token = jwt.encode(
            payload, auth_system.jwt_secret, algorithm=auth_system.jwt_algorithm
        )
        result = auth_system.validate_token(token)
        assert result is None

    def test_validate_token_invalid_session(self, auth_system: Any) -> Any:
        """Test token validation with invalid session"""
        user_id = "123"
        session_id = "invalid_session"
        auth_system._is_session_valid = Mock(return_value=False)
        token = auth_system._generate_access_token(user_id, session_id)
        result = auth_system.validate_token(token)
        assert result is None

    def test_refresh_access_token_success(self, auth_system: Any) -> Any:
        """Test successful token refresh"""
        user_id = "123"
        session_id = "session_123"
        auth_system._is_session_valid = Mock(return_value=True)
        refresh_token = auth_system._generate_refresh_token(user_id, session_id)
        result = auth_system.refresh_access_token(refresh_token)
        assert result is not None
        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert "expires_in" in result

    def test_refresh_access_token_invalid(self, auth_system: Any) -> Any:
        """Test token refresh with invalid token"""
        result = auth_system.refresh_access_token("invalid_token")
        assert result is None

    def test_logout_success(self, auth_system: Any, db_session: Any) -> Any:
        """Test successful logout"""
        session_id = "session_123"
        session = UserSession(
            session_id=session_id,
            user_id=1,
            device_fingerprint="test_device",
            ip_address="127.0.0.1",
            user_agent="test_agent",
            created_at=utc_now(),
            last_activity=utc_now(),
            expires_at=utc_now() + timedelta(hours=24),
            status=SessionStatus.ACTIVE,
            risk_score=0.3,
        )
        db_session.add(session)
        db_session.commit()
        auth_system._revoke_session = Mock()
        result = auth_system.logout(session_id)
        assert result is True
        auth_system._revoke_session.assert_called_once_with(session_id)
        db_session.refresh(session)
        assert session.status == SessionStatus.REVOKED
        assert session.ended_at is not None

    def test_logout_all_sessions(
        self, auth_system: Any, db_session: Any, test_user: Any
    ) -> Any:
        """Test logout from all sessions"""
        sessions = []
        for i in range(3):
            session = UserSession(
                session_id=f"session_{i}",
                user_id=test_user.id,
                device_fingerprint=f"device_{i}",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                created_at=utc_now(),
                last_activity=utc_now(),
                expires_at=utc_now() + timedelta(hours=24),
                status=SessionStatus.ACTIVE,
                risk_score=0.3,
            )
            sessions.append(session)
            db_session.add(session)
        db_session.commit()
        auth_system._revoke_session = Mock()
        result = auth_system.logout_all_sessions(str(test_user.id))
        assert result is True
        assert auth_system._revoke_session.call_count == 3
        for session in sessions:
            db_session.refresh(session)
            assert session.status == SessionStatus.REVOKED
            assert session.ended_at is not None

    def test_get_active_sessions(
        self, auth_system: Any, db_session: Any, test_user: Any
    ) -> Any:
        """Test getting active sessions"""
        active_sessions = []
        for i in range(2):
            session = UserSession(
                session_id=f"active_session_{i}",
                user_id=test_user.id,
                device_fingerprint=f"device_{i}",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                created_at=utc_now(),
                last_activity=utc_now(),
                expires_at=utc_now() + timedelta(hours=24),
                status=SessionStatus.ACTIVE,
                risk_score=0.3,
                location='{"country": "US"}',
            )
            active_sessions.append(session)
            db_session.add(session)
        revoked_session = UserSession(
            session_id="revoked_session",
            user_id=test_user.id,
            device_fingerprint="device_revoked",
            ip_address="127.0.0.1",
            user_agent="test_agent",
            created_at=utc_now(),
            last_activity=utc_now(),
            expires_at=utc_now() + timedelta(hours=24),
            status=SessionStatus.REVOKED,
            risk_score=0.3,
        )
        db_session.add(revoked_session)
        db_session.commit()
        result = auth_system.get_active_sessions(str(test_user.id))
        assert len(result) == 2
        for session_info in result:
            assert isinstance(session_info, SessionInfo)
            assert session_info.user_id == str(test_user.id)
            assert session_info.status == SessionStatus.ACTIVE

    def test_verify_password(self, auth_system: Any) -> Any:
        """Test password verification"""
        password = "TestPassword123!"
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )
        assert auth_system._verify_password(password, hashed) is True
        assert auth_system._verify_password("WrongPassword", hashed) is False

    def test_hash_password(self, auth_system: Any) -> Any:
        """Test password hashing"""
        password = "TestPassword123!"
        hashed = auth_system._hash_password(password)
        assert hashed != password
        assert len(hashed) > 0
        assert auth_system._verify_password(password, hashed) is True

    def test_generate_tokens(self, auth_system: Any) -> Any:
        """Test token generation"""
        user_id = "123"
        session_id = "session_123"
        access_token = auth_system._generate_access_token(user_id, session_id)
        assert access_token is not None
        assert len(access_token) > 0
        payload = jwt.decode(
            access_token, auth_system.jwt_secret, algorithms=[auth_system.jwt_algorithm]
        )
        assert payload["user_id"] == user_id
        assert payload["session_id"] == session_id
        assert payload["type"] == "access"
        refresh_token = auth_system._generate_refresh_token(user_id, session_id)
        assert refresh_token is not None
        assert len(refresh_token) > 0
        payload = jwt.decode(
            refresh_token,
            auth_system.jwt_secret,
            algorithms=[auth_system.jwt_algorithm],
        )
        assert payload["user_id"] == user_id
        assert payload["session_id"] == session_id
        assert payload["type"] == "refresh"

    def test_validate_password_strength(self, auth_system: Any) -> Any:
        """Test password strength validation"""
        result = auth_system.validate_password_strength("StrongPassword123!")
        assert result["valid"] is True
        assert result["strength"] == "Strong"
        assert result["score"] == 5
        assert len(result["issues"]) == 0
        result = auth_system.validate_password_strength("weak")
        assert result["valid"] is False
        assert result["strength"] == "Very Weak"
        assert result["score"] < 5
        assert len(result["issues"]) > 0
        result = auth_system.validate_password_strength("password")
        assert result["valid"] is False
        assert result["score"] == 0
        assert "too common" in " ".join(result["issues"]).lower()


class TestPasswordValidation:
    """Test password validation functionality"""

    def test_strong_password(self, auth_system: Any) -> Any:
        """Test validation of strong password"""
        password = "MyStr0ng!P@ssw0rd"
        result = auth_system.validate_password_strength(password)
        assert result["valid"] is True
        assert result["strength"] == "Strong"
        assert result["score"] == 5
        assert len(result["issues"]) == 0

    def test_weak_passwords(self, auth_system: Any) -> Any:
        """Test validation of various weak passwords"""
        weak_passwords = [
            "short",
            "nouppercase123!",
            "NOLOWERCASE123!",
            "NoNumbers!",
            "NoSpecialChars123",
            "password",
            "123456",
            "qwerty",
        ]
        for password in weak_passwords:
            result = auth_system.validate_password_strength(password)
            assert result["valid"] is False
            assert result["score"] < 5
            assert len(result["issues"]) > 0


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_check_rate_limit_first_request(self, auth_system: Any) -> Any:
        """Test rate limiting for first request"""
        auth_system.redis_client.get.return_value = None
        result = auth_system._check_rate_limit("login", "127.0.0.1")
        assert result is True
        auth_system.redis_client.setex.assert_called_once()

    def test_check_rate_limit_within_limit(self, auth_system: Any) -> Any:
        """Test rate limiting within limit"""
        auth_system.redis_client.get.return_value = "3"
        result = auth_system._check_rate_limit("login", "127.0.0.1")
        assert result is True
        auth_system.redis_client.incr.assert_called_once()

    def test_check_rate_limit_exceeded(self, auth_system: Any) -> Any:
        """Test rate limiting when limit exceeded"""
        auth_system.redis_client.get.return_value = "5"
        result = auth_system._check_rate_limit("login", "127.0.0.1")
        assert result is False
        auth_system.redis_client.incr.assert_not_called()


class TestSessionManagement:
    """Test session management functionality"""

    def test_create_session(self, auth_system, test_user):
        """Test session creation"""
        auth_system._get_location_from_ip = Mock(return_value={"country": "US"})
        session_info = auth_system._create_session(
            test_user, "device_123", "127.0.0.1", "test_agent", 0.3
        )
        assert isinstance(session_info, SessionInfo)
        assert session_info.user_id == str(test_user.id)
        assert session_info.device_fingerprint == "device_123"
        assert session_info.ip_address == "127.0.0.1"
        assert session_info.user_agent == "test_agent"
        assert session_info.risk_score == 0.3
        assert session_info.status == SessionStatus.ACTIVE

    def test_is_session_valid(self, auth_system: Any) -> Any:
        """Test session validation"""
        auth_system.redis_client.get.return_value = '{"user_id": "123"}'
        assert auth_system._is_session_valid("session_123") is True
        auth_system.redis_client.get.return_value = None
        assert auth_system._is_session_valid("invalid_session") is False

    def test_revoke_session(self, auth_system: Any) -> Any:
        """Test session revocation"""
        auth_system._revoke_session("session_123")
        auth_system.redis_client.delete.assert_called_once_with("session:session_123")


class TestSecurityFeatures:
    """Test security-related features"""

    def test_calculate_authentication_risk_new_device(
        self, auth_system, db_session, test_user
    ):
        """Test risk calculation for new device"""
        risk_score = auth_system._calculate_authentication_risk(
            test_user, "new_device", "127.0.0.1", "test_agent"
        )
        assert risk_score >= 0.3

    def test_calculate_authentication_risk_known_device(
        self, auth_system, db_session, test_user
    ):
        """Test risk calculation for known device"""
        for i in range(5):
            session = UserSession(
                session_id=f"session_{i}",
                user_id=test_user.id,
                device_fingerprint="known_device",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                created_at=utc_now(),
                last_activity=utc_now(),
                expires_at=utc_now() + timedelta(hours=24),
                status=SessionStatus.ACTIVE,
                risk_score=0.1,
            )
            db_session.add(session)
        db_session.commit()
        risk_score = auth_system._calculate_authentication_risk(
            test_user, "known_device", "127.0.0.1", "test_agent"
        )
        assert risk_score < 0.3

    def test_is_account_locked_not_locked(
        self, auth_system: Any, test_user: Any
    ) -> Any:
        """Test account lock check when not locked"""
        result = auth_system._is_account_locked(str(test_user.id))
        assert result is False

    def test_is_account_locked_locked(
        self, auth_system: Any, db_session: Any, test_user: Any
    ) -> Any:
        """Test account lock check when locked"""
        for i in range(6):
            attempt = LoginAttempt(
                user_id=test_user.id,
                email=test_user.email,
                ip_address="127.0.0.1",
                success=False,
                details="Invalid password",
                timestamp=utc_now(),
            )
            db_session.add(attempt)
        db_session.commit()
        result = auth_system._is_account_locked(str(test_user.id))
        assert result is True
