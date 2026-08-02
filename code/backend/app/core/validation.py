import logging
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Union

import email_validator
import phonenumbers
from app.core.time_utils import utc_now
from phonenumbers import NumberParseException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error"""

    def __init__(self, message: str, field: str = None, code: str = None) -> None:
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)


class ValidationResult:
    """Result of validation operation"""

    def __init__(
        self, is_valid: bool = True, errors: List[Dict[str, Any]] = None
    ) -> None:
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, field: str, message: str, code: str = None) -> Any:
        """Add validation error"""
        self.is_valid = False
        self.errors.append(
            {"field": field, "message": message, "code": code or "validation_error"}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {"is_valid": self.is_valid, "errors": self.errors}


class FinancialValidator:
    """Validator for financial data and business rules"""

    @staticmethod
    def validate_amount(
        amount: Union[str, float, Decimal],
        min_amount: Decimal = None,
        max_amount: Decimal = None,
        allow_negative: bool = False,
    ) -> ValidationResult:
        """Validate monetary amount"""
        result = ValidationResult()
        try:
            if isinstance(amount, str):
                cleaned_amount = re.sub("[,$€£¥]", "", amount.strip())
                amount = Decimal(cleaned_amount)
            elif isinstance(amount, float):
                amount = Decimal(str(amount))
            elif not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            result.add_error("amount", "Invalid amount format", "invalid_format")
            return result
        if not allow_negative and amount < 0:
            result.add_error("amount", "Amount cannot be negative", "negative_amount")
        if min_amount is not None and amount < min_amount:
            result.add_error(
                "amount", f"Amount must be at least {min_amount}", "below_minimum"
            )
        if max_amount is not None and amount > max_amount:
            result.add_error(
                "amount", f"Amount cannot exceed {max_amount}", "above_maximum"
            )
        if amount.as_tuple().exponent < -2:
            result.add_error(
                "amount",
                "Amount cannot have more than 2 decimal places",
                "too_many_decimals",
            )
        return result

    @staticmethod
    def validate_percentage(
        percentage: Union[str, float, Decimal],
        min_value: Decimal = Decimal("0"),
        max_value: Decimal = Decimal("100"),
    ) -> ValidationResult:
        """Validate percentage value"""
        result = ValidationResult()
        try:
            if isinstance(percentage, str):
                cleaned_percentage = percentage.replace("%", "").strip()
                percentage = Decimal(cleaned_percentage)
            elif isinstance(percentage, float):
                percentage = Decimal(str(percentage))
            elif not isinstance(percentage, Decimal):
                percentage = Decimal(str(percentage))
        except (InvalidOperation, ValueError):
            result.add_error(
                "percentage", "Invalid percentage format", "invalid_format"
            )
            return result
        if percentage < min_value:
            result.add_error(
                "percentage",
                f"Percentage must be at least {min_value}%",
                "below_minimum",
            )
        if percentage > max_value:
            result.add_error(
                "percentage", f"Percentage cannot exceed {max_value}%", "above_maximum"
            )
        return result

    @staticmethod
    def validate_symbol(symbol: str) -> ValidationResult:
        """Validate asset symbol"""
        result = ValidationResult()
        if not symbol or not isinstance(symbol, str):
            result.add_error("symbol", "Symbol is required", "required")
            return result
        symbol = symbol.strip().upper()
        if len(symbol) < 1 or len(symbol) > 10:
            result.add_error(
                "symbol", "Symbol must be 1-10 characters long", "invalid_length"
            )
        if not re.match("^[A-Z0-9]+$", symbol):
            result.add_error(
                "symbol",
                "Symbol can only contain letters and numbers",
                "invalid_format",
            )
        return result

    @staticmethod
    def validate_quantity(
        quantity: Union[str, float, Decimal], min_quantity: Decimal = Decimal("0")
    ) -> ValidationResult:
        """Validate asset quantity"""
        result = ValidationResult()
        try:
            if isinstance(quantity, str):
                quantity = Decimal(quantity.strip())
            elif isinstance(quantity, float):
                quantity = Decimal(str(quantity))
            elif not isinstance(quantity, Decimal):
                quantity = Decimal(str(quantity))
        except (InvalidOperation, ValueError):
            result.add_error("quantity", "Invalid quantity format", "invalid_format")
            return result
        if quantity < min_quantity:
            result.add_error(
                "quantity", f"Quantity must be at least {min_quantity}", "below_minimum"
            )
        if quantity.as_tuple().exponent < -8:
            result.add_error(
                "quantity",
                "Quantity cannot have more than 8 decimal places",
                "too_many_decimals",
            )
        return result

    @staticmethod
    def validate_portfolio_allocation(
        allocations: Dict[str, Decimal],
    ) -> ValidationResult:
        """Validate portfolio allocation percentages"""
        result = ValidationResult()
        if not allocations:
            result.add_error(
                "allocations", "At least one allocation is required", "required"
            )
            return result
        total_allocation = sum(allocations.values())
        for asset, allocation in allocations.items():
            if allocation < 0:
                result.add_error(
                    f"allocation_{asset}",
                    "Allocation cannot be negative",
                    "negative_allocation",
                )
            if allocation > 100:
                result.add_error(
                    f"allocation_{asset}",
                    "Allocation cannot exceed 100%",
                    "excessive_allocation",
                )
        if abs(total_allocation - 100) > Decimal("0.01"):
            result.add_error(
                "total_allocation", "Total allocation must equal 100%", "invalid_total"
            )
        return result


class UserValidator:
    """Validator for user data"""

    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Validate email address"""
        result = ValidationResult()
        if not email or not isinstance(email, str):
            result.add_error("email", "Email is required", "required")
            return result
        try:
            valid_email = email_validator.validate_email(email)
            if len(valid_email.email) > 254:
                result.add_error("email", "Email address is too long", "too_long")
        except email_validator.EmailNotValidError as e:
            result.add_error("email", str(e), "invalid_format")
        return result

    @staticmethod
    def validate_phone_number(phone: str, country_code: str = None) -> ValidationResult:
        """Validate phone number"""
        result = ValidationResult()
        if not phone or not isinstance(phone, str):
            result.add_error("phone", "Phone number is required", "required")
            return result
        try:
            parsed_number = phonenumbers.parse(phone, country_code)
            if not phonenumbers.is_valid_number(parsed_number):
                result.add_error("phone", "Invalid phone number", "invalid_format")
        except NumberParseException as e:
            result.add_error("phone", f"Invalid phone number: {e}", "invalid_format")
        return result

    @staticmethod
    def validate_name(name: str, field_name: str = "name") -> ValidationResult:
        """Validate person name"""
        result = ValidationResult()
        if not name or not isinstance(name, str):
            result.add_error(
                field_name, f"{field_name.title()} is required", "required"
            )
            return result
        name = name.strip()
        if len(name) < 1:
            result.add_error(
                field_name, f"{field_name.title()} cannot be empty", "empty"
            )
        elif len(name) > 50:
            result.add_error(
                field_name,
                f"{field_name.title()} is too long (max 50 characters)",
                "too_long",
            )
        if not re.match("^[a-zA-Z\\s\\-']+$", name):
            result.add_error(
                field_name,
                f"{field_name.title()} contains invalid characters",
                "invalid_characters",
            )
        return result

    @staticmethod
    def validate_username(username: str) -> ValidationResult:
        """Validate username"""
        result = ValidationResult()
        if not username or not isinstance(username, str):
            result.add_error("username", "Username is required", "required")
            return result
        username = username.strip()
        if len(username) < 3:
            result.add_error(
                "username", "Username must be at least 3 characters long", "too_short"
            )
        elif len(username) > 30:
            result.add_error(
                "username", "Username is too long (max 30 characters)", "too_long"
            )
        if not re.match("^[a-zA-Z0-9_-]+$", username):
            result.add_error(
                "username",
                "Username can only contain letters, numbers, underscores, and hyphens",
                "invalid_format",
            )
        if username.startswith(("_", "-")) or username.endswith(("_", "-")):
            result.add_error(
                "username",
                "Username cannot start or end with underscore or hyphen",
                "invalid_format",
            )
        return result

    @staticmethod
    def validate_date_of_birth(dob: Union[str, date, datetime]) -> ValidationResult:
        """Validate date of birth"""
        result = ValidationResult()
        if not dob:
            result.add_error("date_of_birth", "Date of birth is required", "required")
            return result
        try:
            if isinstance(dob, str):
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                    try:
                        dob = datetime.strptime(dob, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    result.add_error(
                        "date_of_birth", "Invalid date format", "invalid_format"
                    )
                    return result
            elif isinstance(dob, datetime):
                dob = dob.date()
        except (ValueError, TypeError):
            result.add_error("date_of_birth", "Invalid date format", "invalid_format")
            return result
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            result.add_error(
                "date_of_birth", "Must be at least 18 years old", "too_young"
            )
        elif age > 120:
            result.add_error("date_of_birth", "Invalid date of birth", "invalid_age")
        return result


class SecurityValidator:
    """Validator for security-related data"""

    @staticmethod
    def validate_ip_address(ip: str) -> ValidationResult:
        """Validate IP address"""
        result = ValidationResult()
        if not ip or not isinstance(ip, str):
            result.add_error("ip_address", "IP address is required", "required")
            return result
        ipv4_pattern = "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        ipv6_pattern = "^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
        if not (re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip)):
            result.add_error(
                "ip_address", "Invalid IP address format", "invalid_format"
            )
        return result

    @staticmethod
    def validate_api_key_name(name: str) -> ValidationResult:
        """Validate API key name"""
        result = ValidationResult()
        if not name or not isinstance(name, str):
            result.add_error("name", "API key name is required", "required")
            return result
        name = name.strip()
        if len(name) < 3:
            result.add_error(
                "name", "API key name must be at least 3 characters long", "too_short"
            )
        elif len(name) > 50:
            result.add_error(
                "name", "API key name is too long (max 50 characters)", "too_long"
            )
        if not re.match("^[a-zA-Z0-9\\s\\-_]+$", name):
            result.add_error(
                "name", "API key name contains invalid characters", "invalid_characters"
            )
        return result


class TransactionValidator:
    """Validator for transaction data"""

    @staticmethod
    def validate_transaction_type(
        transaction_type: str, valid_types: List[str]
    ) -> ValidationResult:
        """Validate transaction type"""
        result = ValidationResult()
        if not transaction_type:
            result.add_error(
                "transaction_type", "Transaction type is required", "required"
            )
            return result
        if transaction_type not in valid_types:
            result.add_error(
                "transaction_type",
                f"Invalid transaction type. Must be one of: {', '.join(valid_types)}",
                "invalid_type",
            )
        return result

    @staticmethod
    def validate_buy_transaction(
        quantity: Decimal, price: Decimal, available_balance: Decimal
    ) -> ValidationResult:
        """Validate buy transaction"""
        result = ValidationResult()
        quantity_result = FinancialValidator.validate_quantity(
            quantity, Decimal("0.00000001")
        )
        if not quantity_result.is_valid:
            result.errors.extend(quantity_result.errors)
        price_result = FinancialValidator.validate_amount(price, Decimal("0.01"))
        if not price_result.is_valid:
            result.errors.extend(price_result.errors)
        if quantity_result.is_valid and price_result.is_valid:
            total_cost = quantity * price
            if total_cost > available_balance:
                result.add_error(
                    "balance",
                    "Insufficient balance for this transaction",
                    "insufficient_balance",
                )
        result.is_valid = len(result.errors) == 0
        return result

    @staticmethod
    def validate_sell_transaction(
        quantity: Decimal, price: Decimal, available_quantity: Decimal
    ) -> ValidationResult:
        """Validate sell transaction"""
        result = ValidationResult()
        quantity_result = FinancialValidator.validate_quantity(
            quantity, Decimal("0.00000001")
        )
        if not quantity_result.is_valid:
            result.errors.extend(quantity_result.errors)
        price_result = FinancialValidator.validate_amount(price, Decimal("0.01"))
        if not price_result.is_valid:
            result.errors.extend(price_result.errors)
        if quantity_result.is_valid and quantity > available_quantity:
            result.add_error(
                "quantity",
                "Insufficient quantity available for sale",
                "insufficient_quantity",
            )
        result.is_valid = len(result.errors) == 0
        return result


class ComplianceValidator:
    """Validator for compliance and regulatory requirements"""

    @staticmethod
    def validate_large_transaction(
        amount: Decimal, threshold: Decimal = Decimal("10000")
    ) -> ValidationResult:
        """Validate large transactions that may require additional reporting"""
        result = ValidationResult()
        if amount >= threshold:
            logger.info(
                f"Large transaction detected: {amount}", extra={"compliance": True}
            )
        return result

    @staticmethod
    def validate_suspicious_pattern(
        user_id: str, transaction_history: List[Dict]
    ) -> ValidationResult:
        """Validate for suspicious transaction patterns"""
        result = ValidationResult()
        if len(transaction_history) > 10:
            rapid_transactions = [
                t
                for t in transaction_history
                if (utc_now() - t["timestamp"]).total_seconds() < 3600
            ]
            if len(rapid_transactions) > 5:
                result.add_error(
                    "pattern",
                    "Suspicious transaction pattern detected",
                    "suspicious_pattern",
                )
                logger.warning(
                    f"Suspicious pattern detected for user {user_id}",
                    extra={"security": True, "user_id": user_id},
                )
        return result


class CompositeValidator:
    """Main validator that combines all validation logic"""

    def __init__(self) -> None:
        self.financial = FinancialValidator()
        self.user = UserValidator()
        self.security = SecurityValidator()
        self.transaction = TransactionValidator()
        self.compliance = ComplianceValidator()

    def validate_user_registration(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate user registration data"""
        result = ValidationResult()
        email_result = self.user.validate_email(data.get("email"))
        if not email_result.is_valid:
            result.errors.extend(email_result.errors)
        first_name_result = self.user.validate_name(
            data.get("first_name"), "first_name"
        )
        if not first_name_result.is_valid:
            result.errors.extend(first_name_result.errors)
        last_name_result = self.user.validate_name(data.get("last_name"), "last_name")
        if not last_name_result.is_valid:
            result.errors.extend(last_name_result.errors)
        if data.get("username"):
            username_result = self.user.validate_username(data.get("username"))
            if not username_result.is_valid:
                result.errors.extend(username_result.errors)
        if data.get("phone_number"):
            phone_result = self.user.validate_phone_number(
                data.get("phone_number"), data.get("country")
            )
            if not phone_result.is_valid:
                result.errors.extend(phone_result.errors)
        if data.get("date_of_birth"):
            dob_result = self.user.validate_date_of_birth(data.get("date_of_birth"))
            if not dob_result.is_valid:
                result.errors.extend(dob_result.errors)
        result.is_valid = len(result.errors) == 0
        return result

    def validate_portfolio_creation(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate portfolio creation data"""
        result = ValidationResult()
        name = data.get("name", "").strip()
        if not name:
            result.add_error("name", "Portfolio name is required", "required")
        elif len(name) > 100:
            result.add_error(
                "name", "Portfolio name is too long (max 100 characters)", "too_long"
            )
        if data.get("allocations"):
            allocation_result = self.financial.validate_portfolio_allocation(
                data["allocations"]
            )
            if not allocation_result.is_valid:
                result.errors.extend(allocation_result.errors)
        result.is_valid = len(result.errors) == 0
        return result

    def validate_trade_order(
        self, data: Dict[str, Any], user_context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate trade order"""
        result = ValidationResult()
        valid_types = ["buy", "sell"]
        type_result = self.transaction.validate_transaction_type(
            data.get("transaction_type"), valid_types
        )
        if not type_result.is_valid:
            result.errors.extend(type_result.errors)
        symbol_result = self.financial.validate_symbol(data.get("symbol", ""))
        if not symbol_result.is_valid:
            result.errors.extend(symbol_result.errors)
        if data.get("transaction_type") == "buy":
            buy_result = self.transaction.validate_buy_transaction(
                Decimal(str(data.get("quantity", 0))),
                Decimal(str(data.get("price", 0))),
                Decimal(str(user_context.get("available_balance", 0))),
            )
            if not buy_result.is_valid:
                result.errors.extend(buy_result.errors)
        elif data.get("transaction_type") == "sell":
            sell_result = self.transaction.validate_sell_transaction(
                Decimal(str(data.get("quantity", 0))),
                Decimal(str(data.get("price", 0))),
                Decimal(str(user_context.get("available_quantity", 0))),
            )
            if not sell_result.is_valid:
                result.errors.extend(sell_result.errors)
        amount = Decimal(str(data.get("quantity", 0))) * Decimal(
            str(data.get("price", 0))
        )
        compliance_result = self.compliance.validate_large_transaction(amount)
        if not compliance_result.is_valid:
            result.errors.extend(compliance_result.errors)
        result.is_valid = len(result.errors) == 0
        return result


validator = CompositeValidator()
