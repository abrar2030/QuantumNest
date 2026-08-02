import base64
import json
import logging
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import bcrypt
import pyotp
from app.core.config import get_settings
from app.core.time_utils import utc_now
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class EncryptionMethod(str, Enum):
    FERNET = "fernet"
    AES_GCM = "aes_gcm"
    AES_CBC = "aes_cbc"
    RSA = "rsa"
    HYBRID = "hybrid"


class KeyDerivationMethod(str, Enum):
    PBKDF2 = "pbkdf2"
    SCRYPT = "scrypt"
    BCRYPT = "bcrypt"


@dataclass
class EncryptionResult:
    """Encryption result with metadata"""

    encrypted_data: bytes
    method: EncryptionMethod
    key_id: Optional[str] = None
    iv: Optional[bytes] = None
    salt: Optional[bytes] = None
    tag: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class KeyInfo:
    """Key information"""

    key_id: str
    key_type: str
    created_at: datetime
    expires_at: Optional[datetime]
    algorithm: str
    key_size: int
    usage: List[str]
    metadata: Dict[str, Any]


class AdvancedEncryptionManager:
    """Advanced encryption manager with multiple algorithms and key management"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = logging.get_logger(__name__)
        self.keys = {}
        self.key_metadata = {}
        self.default_method = EncryptionMethod.AES_GCM
        self.key_rotation_interval = timedelta(days=90)
        self.master_key = self._get_or_create_master_key()
        self._initialize_default_keys()

    def encrypt(
        self,
        data: Union[str, bytes],
        method: EncryptionMethod = None,
        key_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EncryptionResult:
        """Encrypt data using specified method"""
        try:
            if isinstance(data, str):
                data = data.encode("utf-8")
            method = method or self.default_method
            if method == EncryptionMethod.FERNET:
                return self._encrypt_fernet(data, key_id, metadata)
            elif method == EncryptionMethod.AES_GCM:
                return self._encrypt_aes_gcm(data, key_id, metadata)
            elif method == EncryptionMethod.AES_CBC:
                return self._encrypt_aes_cbc(data, key_id, metadata)
            elif method == EncryptionMethod.RSA:
                return self._encrypt_rsa(data, key_id, metadata)
            elif method == EncryptionMethod.HYBRID:
                return self._encrypt_hybrid(data, key_id, metadata)
            else:
                raise ValueError(f"Unsupported encryption method: {method}")
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}", exc_info=True)
            raise

    def decrypt(
        self, encrypted_result: EncryptionResult, key_id: Optional[str] = None
    ) -> bytes:
        """Decrypt data using the method specified in the result"""
        try:
            method = encrypted_result.method
            if method == EncryptionMethod.FERNET:
                return self._decrypt_fernet(encrypted_result, key_id)
            elif method == EncryptionMethod.AES_GCM:
                return self._decrypt_aes_gcm(encrypted_result, key_id)
            elif method == EncryptionMethod.AES_CBC:
                return self._decrypt_aes_cbc(encrypted_result, key_id)
            elif method == EncryptionMethod.RSA:
                return self._decrypt_rsa(encrypted_result, key_id)
            elif method == EncryptionMethod.HYBRID:
                return self._decrypt_hybrid(encrypted_result, key_id)
            else:
                raise ValueError(f"Unsupported decryption method: {method}")
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}", exc_info=True)
            raise

    def _encrypt_fernet(
        self, data: bytes, key_id: Optional[str], metadata: Optional[Dict[str, Any]]
    ) -> EncryptionResult:
        """Encrypt using Fernet (symmetric)"""
        key_id = key_id or "default_fernet"
        if key_id not in self.keys:
            self._generate_fernet_key(key_id)
        fernet = Fernet(self.keys[key_id])
        encrypted_data = fernet.encrypt(data)
        return EncryptionResult(
            encrypted_data=encrypted_data,
            method=EncryptionMethod.FERNET,
            key_id=key_id,
            metadata=metadata,
        )

    def _decrypt_fernet(
        self, encrypted_result: EncryptionResult, key_id: Optional[str]
    ) -> bytes:
        """Decrypt using Fernet"""
        key_id = key_id or encrypted_result.key_id or "default_fernet"
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")
        fernet = Fernet(self.keys[key_id])
        return fernet.decrypt(encrypted_result.encrypted_data)

    def _encrypt_aes_gcm(
        self, data: bytes, key_id: Optional[str], metadata: Optional[Dict[str, Any]]
    ) -> EncryptionResult:
        """Encrypt using AES-GCM"""
        key_id = key_id or "default_aes"
        if key_id not in self.keys:
            self._generate_aes_key(key_id)
        iv = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(self.keys[key_id]), modes.GCM(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        return EncryptionResult(
            encrypted_data=encrypted_data,
            method=EncryptionMethod.AES_GCM,
            key_id=key_id,
            iv=iv,
            tag=encryptor.tag,
            metadata=metadata,
        )

    def _decrypt_aes_gcm(
        self, encrypted_result: EncryptionResult, key_id: Optional[str]
    ) -> bytes:
        """Decrypt using AES-GCM"""
        key_id = key_id or encrypted_result.key_id or "default_aes"
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")
        cipher = Cipher(
            algorithms.AES(self.keys[key_id]),
            modes.GCM(encrypted_result.iv, encrypted_result.tag),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_result.encrypted_data) + decryptor.finalize()

    def _encrypt_aes_cbc(
        self, data: bytes, key_id: Optional[str], metadata: Optional[Dict[str, Any]]
    ) -> EncryptionResult:
        """Encrypt using AES-CBC with PKCS7 padding"""
        key_id = key_id or "default_aes"
        if key_id not in self.keys:
            self._generate_aes_key(key_id)
        iv = os.urandom(16)
        padded_data = pad(data, AES.block_size)
        cipher = Cipher(
            algorithms.AES(self.keys[key_id]), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return EncryptionResult(
            encrypted_data=encrypted_data,
            method=EncryptionMethod.AES_CBC,
            key_id=key_id,
            iv=iv,
            metadata=metadata,
        )

    def _decrypt_aes_cbc(
        self, encrypted_result: EncryptionResult, key_id: Optional[str]
    ) -> bytes:
        """Decrypt using AES-CBC"""
        key_id = key_id or encrypted_result.key_id or "default_aes"
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")
        cipher = Cipher(
            algorithms.AES(self.keys[key_id]),
            modes.CBC(encrypted_result.iv),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        padded_data = (
            decryptor.update(encrypted_result.encrypted_data) + decryptor.finalize()
        )
        return unpad(padded_data, AES.block_size)

    def _encrypt_rsa(
        self, data: bytes, key_id: Optional[str], metadata: Optional[Dict[str, Any]]
    ) -> EncryptionResult:
        """Encrypt using RSA (for small data)"""
        key_id = key_id or "default_rsa"
        if key_id not in self.keys:
            self._generate_rsa_key_pair(key_id)
        public_key = self.keys[f"{key_id}_public"]
        if len(data) > 190:
            raise ValueError(
                "Data too large for RSA encryption. Use hybrid encryption instead."
            )
        encrypted_data = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return EncryptionResult(
            encrypted_data=encrypted_data,
            method=EncryptionMethod.RSA,
            key_id=key_id,
            metadata=metadata,
        )

    def _decrypt_rsa(
        self, encrypted_result: EncryptionResult, key_id: Optional[str]
    ) -> bytes:
        """Decrypt using RSA"""
        key_id = key_id or encrypted_result.key_id or "default_rsa"
        private_key_id = f"{key_id}_private"
        if private_key_id not in self.keys:
            raise ValueError(f"Private key {private_key_id} not found")
        private_key = self.keys[private_key_id]
        return private_key.decrypt(
            encrypted_result.encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def _encrypt_hybrid(
        self, data: bytes, key_id: Optional[str], metadata: Optional[Dict[str, Any]]
    ) -> EncryptionResult:
        """Encrypt using hybrid encryption (RSA + AES)"""
        key_id = key_id or "default_hybrid"
        aes_key = os.urandom(32)
        aes_result = self._encrypt_aes_gcm_with_key(data, aes_key)
        rsa_key_id = f"{key_id}_rsa"
        if rsa_key_id not in self.keys:
            self._generate_rsa_key_pair(rsa_key_id)
        encrypted_aes_key = self._encrypt_rsa(aes_key, rsa_key_id, None).encrypted_data
        combined_data = (
            len(encrypted_aes_key).to_bytes(4, "big")
            + encrypted_aes_key
            + aes_result.encrypted_data
        )
        return EncryptionResult(
            encrypted_data=combined_data,
            method=EncryptionMethod.HYBRID,
            key_id=key_id,
            iv=aes_result.iv,
            tag=aes_result.tag,
            metadata=metadata,
        )

    def _decrypt_hybrid(
        self, encrypted_result: EncryptionResult, key_id: Optional[str]
    ) -> bytes:
        """Decrypt using hybrid encryption"""
        key_id = key_id or encrypted_result.key_id or "default_hybrid"
        key_length = int.from_bytes(encrypted_result.encrypted_data[:4], "big")
        encrypted_aes_key = encrypted_result.encrypted_data[4 : 4 + key_length]
        encrypted_data = encrypted_result.encrypted_data[4 + key_length :]
        rsa_key_id = f"{key_id}_rsa"
        rsa_result = EncryptionResult(
            encrypted_data=encrypted_aes_key,
            method=EncryptionMethod.RSA,
            key_id=rsa_key_id,
        )
        aes_key = self._decrypt_rsa(rsa_result, rsa_key_id)
        return self._decrypt_aes_gcm_with_key(
            encrypted_data, aes_key, encrypted_result.iv, encrypted_result.tag
        )

    def _encrypt_aes_gcm_with_key(self, data: bytes, key: bytes) -> EncryptionResult:
        """Encrypt with specific AES key"""
        iv = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        return EncryptionResult(
            encrypted_data=encrypted_data,
            method=EncryptionMethod.AES_GCM,
            iv=iv,
            tag=encryptor.tag,
        )

    def _decrypt_aes_gcm_with_key(
        self, encrypted_data: bytes, key: bytes, iv: bytes, tag: bytes
    ) -> bytes:
        """Decrypt with specific AES key"""
        cipher = Cipher(
            algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()

    def _generate_fernet_key(self, key_id: str) -> Any:
        """Generate Fernet key"""
        key = Fernet.generate_key()
        self.keys[key_id] = key
        self.key_metadata[key_id] = KeyInfo(
            key_id=key_id,
            key_type="fernet",
            created_at=utc_now(),
            expires_at=utc_now() + self.key_rotation_interval,
            algorithm="Fernet",
            key_size=256,
            usage=["encrypt", "decrypt"],
            metadata={},
        )

    def _generate_aes_key(self, key_id: str, key_size: int = 256) -> Any:
        """Generate AES key"""
        key = os.urandom(key_size // 8)
        self.keys[key_id] = key
        self.key_metadata[key_id] = KeyInfo(
            key_id=key_id,
            key_type="aes",
            created_at=utc_now(),
            expires_at=utc_now() + self.key_rotation_interval,
            algorithm=f"AES-{key_size}",
            key_size=key_size,
            usage=["encrypt", "decrypt"],
            metadata={},
        )

    def _generate_rsa_key_pair(self, key_id: str, key_size: int = 2048) -> Any:
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_size, backend=default_backend()
        )
        public_key = private_key.public_key()
        self.keys[f"{key_id}_private"] = private_key
        self.keys[f"{key_id}_public"] = public_key
        for key_type in ["private", "public"]:
            full_key_id = f"{key_id}_{key_type}"
            self.key_metadata[full_key_id] = KeyInfo(
                key_id=full_key_id,
                key_type=f"rsa_{key_type}",
                created_at=utc_now(),
                expires_at=utc_now() + self.key_rotation_interval,
                algorithm=f"RSA-{key_size}",
                key_size=key_size,
                usage=["encrypt", "decrypt"] if key_type == "private" else ["encrypt"],
                metadata={},
            )

    def _get_or_create_master_key(self) -> bytes:
        """Get or create master key for key encryption"""
        master_key_path = os.path.join(os.getcwd(), ".master_key")
        if os.path.exists(master_key_path):
            with open(master_key_path, "rb") as f:
                return f.read()
        else:
            master_key = os.urandom(32)
            with open(master_key_path, "wb") as f:
                f.write(master_key)
            os.chmod(master_key_path, 384)
            return master_key

    def _initialize_default_keys(self) -> Any:
        """Initialize default encryption keys"""
        self._generate_fernet_key("default_fernet")
        self._generate_aes_key("default_aes")
        self._generate_rsa_key_pair("default_rsa")
        self._generate_rsa_key_pair("default_hybrid_rsa")

    def rotate_key(self, key_id: str) -> bool:
        """Rotate encryption key"""
        try:
            if key_id not in self.key_metadata:
                return False
            key_info = self.key_metadata[key_id]
            if key_info.key_type == "fernet":
                self._generate_fernet_key(f"{key_id}_new")
            elif key_info.key_type == "aes":
                self._generate_aes_key(f"{key_id}_new", key_info.key_size)
            elif key_info.key_type.startswith("rsa"):
                base_key_id = key_id.replace("_private", "").replace("_public", "")
                self._generate_rsa_key_pair(f"{base_key_id}_new", key_info.key_size)
            self.logger.info(f"Key {key_id} rotated successfully")
            return True
        except Exception as e:
            self.logger.error(f"Key rotation error: {str(e)}")
            return False

    def get_key_info(self, key_id: str) -> Optional[KeyInfo]:
        """Get key information"""
        return self.key_metadata.get(key_id)

    def list_keys(self) -> List[KeyInfo]:
        """List all keys"""
        return list(self.key_metadata.values())

    def export_public_key(self, key_id: str) -> Optional[str]:
        """Export public key in PEM format"""
        try:
            public_key_id = f"{key_id}_public"
            if public_key_id not in self.keys:
                return None
            public_key = self.keys[public_key_id]
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return pem.decode("utf-8")
        except Exception as e:
            self.logger.error(f"Public key export error: {str(e)}")
            return None


class PasswordManager:
    """Advanced password hashing and verification"""

    def __init__(self) -> None:
        self.logger = logging.get_logger(__name__)
        self.bcrypt_rounds = 12
        self.scrypt_n = 2**14
        self.scrypt_r = 8
        self.scrypt_p = 1
        self.pbkdf2_iterations = 100000

    def hash_password(
        self, password: str, method: KeyDerivationMethod = KeyDerivationMethod.BCRYPT
    ) -> str:
        """Hash password using specified method"""
        try:
            if method == KeyDerivationMethod.BCRYPT:
                return self._hash_bcrypt(password)
            elif method == KeyDerivationMethod.SCRYPT:
                return self._hash_scrypt(password)
            elif method == KeyDerivationMethod.PBKDF2:
                return self._hash_pbkdf2(password)
            else:
                raise ValueError(f"Unsupported hashing method: {method}")
        except Exception as e:
            self.logger.error(f"Password hashing error: {str(e)}")
            raise

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            if hashed_password.startswith("$2b$"):
                return self._verify_bcrypt(password, hashed_password)
            elif hashed_password.startswith("scrypt$"):
                return self._verify_scrypt(password, hashed_password)
            elif hashed_password.startswith("pbkdf2$"):
                return self._verify_pbkdf2(password, hashed_password)
            else:
                return self._verify_bcrypt(password, hashed_password)
        except Exception as e:
            self.logger.error(f"Password verification error: {str(e)}")
            return False

    def _hash_bcrypt(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def _verify_bcrypt(self, password: str, hashed_password: str) -> bool:
        """Verify bcrypt password"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def _hash_scrypt(self, password: str) -> str:
        """Hash password with scrypt"""
        salt = os.urandom(32)
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            n=self.scrypt_n,
            r=self.scrypt_r,
            p=self.scrypt_p,
            backend=default_backend(),
        )
        key = kdf.derive(password.encode("utf-8"))
        return f"scrypt${self.scrypt_n}${self.scrypt_r}${self.scrypt_p}${base64.b64encode(salt).decode()}${base64.b64encode(key).decode()}"

    def _verify_scrypt(self, password: str, hashed_password: str) -> bool:
        """Verify scrypt password"""
        parts = hashed_password.split("$")
        if len(parts) != 6 or parts[0] != "scrypt":
            return False
        n, r, p = (int(parts[1]), int(parts[2]), int(parts[3]))
        salt = base64.b64decode(parts[4])
        expected_key = base64.b64decode(parts[5])
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            n=n,
            r=r,
            p=p,
            backend=default_backend(),
        )
        try:
            kdf.verify(password.encode("utf-8"), expected_key)
            return True
        except Exception:
            return False

    def _hash_pbkdf2(self, password: str) -> str:
        """Hash password with PBKDF2"""
        salt = os.urandom(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.pbkdf2_iterations,
            backend=default_backend(),
        )
        key = kdf.derive(password.encode("utf-8"))
        return f"pbkdf2${self.pbkdf2_iterations}${base64.b64encode(salt).decode()}${base64.b64encode(key).decode()}"

    def _verify_pbkdf2(self, password: str, hashed_password: str) -> bool:
        """Verify PBKDF2 password"""
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2":
            return False
        iterations = int(parts[1])
        salt = base64.b64decode(parts[2])
        expected_key = base64.b64decode(parts[3])
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        try:
            kdf.verify(password.encode("utf-8"), expected_key)
            return True
        except Exception:
            return False


class TokenManager:
    """Secure token generation and management"""

    def __init__(self) -> None:
        self.logger = logging.get_logger(__name__)

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)

    def generate_api_key(self, prefix: str = "qn") -> str:
        """Generate API key with prefix"""
        token = self.generate_secure_token(32)
        return f"{prefix}_{token}"

    def generate_session_id(self) -> str:
        """Generate session ID"""
        return self.generate_secure_token(48)

    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return self.generate_secure_token(24)

    def generate_otp_secret(self) -> str:
        """Generate OTP secret"""
        return pyotp.random_base32()

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for 2FA"""
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append(f"{code[:4]}-{code[4:]}")
        return codes


class DataMasking:
    """Data masking and anonymization utilities"""

    def __init__(self) -> None:
        self.logger = logging.get_logger(__name__)

    def mask_email(self, email: str) -> str:
        """Mask email address"""
        try:
            local, domain = email.split("@")
            if len(local) <= 2:
                masked_local = "*" * len(local)
            else:
                masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
            domain_parts = domain.split(".")
            if len(domain_parts[0]) <= 2:
                masked_domain = "*" * len(domain_parts[0])
            else:
                masked_domain = (
                    domain_parts[0][0]
                    + "*" * (len(domain_parts[0]) - 2)
                    + domain_parts[0][-1]
                )
            return f"{masked_local}@{masked_domain}.{'.'.join(domain_parts[1:])}"
        except Exception:
            return "***@***.***"

    def mask_phone(self, phone: str) -> str:
        """Mask phone number"""
        try:
            digits = "".join(filter(str.isdigit, phone))
            if len(digits) >= 10:
                return f"***-***-{digits[-4:]}"
            else:
                return "***-***-****"
        except Exception:
            return "***-***-****"

    def mask_ssn(self, ssn: str) -> str:
        """Mask Social Security Number"""
        try:
            digits = "".join(filter(str.isdigit, ssn))
            if len(digits) == 9:
                return f"***-**-{digits[-4:]}"
            else:
                return "***-**-****"
        except Exception:
            return "***-**-****"

    def mask_credit_card(self, card_number: str) -> str:
        """Mask credit card number"""
        try:
            digits = "".join(filter(str.isdigit, card_number))
            if len(digits) >= 12:
                return f"****-****-****-{digits[-4:]}"
            else:
                return "****-****-****-****"
        except Exception:
            return "****-****-****-****"

    def mask_account_number(self, account_number: str) -> str:
        """Mask account number"""
        try:
            if len(account_number) <= 4:
                return "*" * len(account_number)
            else:
                return "*" * (len(account_number) - 4) + account_number[-4:]
        except Exception:
            return "****"


encryption_manager = AdvancedEncryptionManager()
password_manager = PasswordManager()
token_manager = TokenManager()
data_masking = DataMasking()


def encrypt_sensitive_data(
    data: Union[str, Dict[str, Any]],
    method: EncryptionMethod = EncryptionMethod.AES_GCM,
) -> str:
    """Encrypt sensitive data and return base64 encoded result"""
    try:
        if isinstance(data, dict):
            data = json.dumps(data)
        result = encryption_manager.encrypt(data, method)
        serializable_result = {
            "encrypted_data": base64.b64encode(result.encrypted_data).decode(),
            "method": result.method.value,
            "key_id": result.key_id,
            "iv": base64.b64encode(result.iv).decode() if result.iv else None,
            "tag": base64.b64encode(result.tag).decode() if result.tag else None,
            "salt": base64.b64encode(result.salt).decode() if result.salt else None,
            "metadata": result.metadata,
        }
        return base64.b64encode(json.dumps(serializable_result).encode()).decode()
    except Exception as e:
        logger.error(f"Data encryption error: {str(e)}")
        raise


def decrypt_sensitive_data(encrypted_data: str) -> Union[str, Dict[str, Any]]:
    """Decrypt sensitive data from base64 encoded result"""
    try:
        serialized_result = json.loads(base64.b64decode(encrypted_data).decode())
        result = EncryptionResult(
            encrypted_data=base64.b64decode(serialized_result["encrypted_data"]),
            method=EncryptionMethod(serialized_result["method"]),
            key_id=serialized_result["key_id"],
            iv=(
                base64.b64decode(serialized_result["iv"])
                if serialized_result["iv"]
                else None
            ),
            tag=(
                base64.b64decode(serialized_result["tag"])
                if serialized_result["tag"]
                else None
            ),
            salt=(
                base64.b64decode(serialized_result["salt"])
                if serialized_result["salt"]
                else None
            ),
            metadata=serialized_result["metadata"],
        )
        decrypted_data = encryption_manager.decrypt(result)
        decrypted_str = decrypted_data.decode("utf-8")
        try:
            return json.loads(decrypted_str)
        except Exception:
            return decrypted_str
    except Exception as e:
        logger.error(f"Data decryption error: {str(e)}")
        raise


def hash_password(password: str) -> str:
    """Hash password using default method"""
    return password_manager.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return password_manager.verify_password(password, hashed_password)


def generate_secure_token(length: int = 32) -> str:
    """Generate secure token"""
    return token_manager.generate_secure_token(length)


def mask_sensitive_data(data: str, data_type: str) -> str:
    """Mask sensitive data based on type"""
    if data_type == "email":
        return data_masking.mask_email(data)
    elif data_type == "phone":
        return data_masking.mask_phone(data)
    elif data_type == "ssn":
        return data_masking.mask_ssn(data)
    elif data_type == "credit_card":
        return data_masking.mask_credit_card(data)
    elif data_type == "account_number":
        return data_masking.mask_account_number(data)
    else:
        return data
