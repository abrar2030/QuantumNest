"""Role-based access control (RBAC) — not wired into the live application.

This module is only imported by ``app/main_flask.py``, which is itself dead
code (see that file's docstring). The live FastAPI app (``app/main.py`` and
``app/api/*.py``) uses a simpler flat role check instead
(``User.role`` — a plain ``UserRole`` string column, checked directly by
each endpoint's dependency).

This module was scaffolded for a fuller RBAC system but the database schema
it depends on was never built: it imports ``Permission``, ``Role``, and
``RolePermission`` ORM models, plus a ``UserRole`` *join-table* model — none
of which exist in ``app/models/models.py``. The only ``UserRole`` that
exists there is the simple string enum used by the flat-role check above,
not an ORM-mapped table, so the queries in this file
(``self.db.query(Permission)``, ``self.db.query(UserRole)...``, etc.) would
raise at runtime if this module were ever imported and exercised.

To complete this module: add ``Permission``, ``Role``, and
``RolePermission`` tables (with a migration) and a ``UserRole`` join-table
model distinct from the existing enum, then wire this module's
``AuthorizationService`` into the FastAPI dependencies in place of the flat
role check.
"""

import functools
import logging
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.core.time_utils import utc_now
from app.models.models import Permission, Role, RolePermission, UserRole
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    USER = "user"
    ACCOUNT = "account"
    TRANSACTION = "transaction"
    PORTFOLIO = "portfolio"
    MARKET_DATA = "market_data"
    REPORT = "report"
    ADMIN = "admin"
    SYSTEM = "system"


class Action(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"
    IMPORT = "import"


class AccessLevel(str, Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass
class AccessRequest:
    """Access request for authorization"""

    user_id: str
    resource: ResourceType
    action: Action
    resource_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class AuthorizationResult:
    """Authorization result"""

    granted: bool
    reason: str
    required_permissions: List[str]
    user_permissions: List[str]
    conditions_met: bool
    risk_level: str


class RoleBasedAccessControl:
    """Role-Based Access Control (RBAC) system"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = logging.get_logger(__name__)
        self.permission_cache = {}
        self.cache_ttl = timedelta(minutes=15)
        self.last_cache_update = {}
        self.default_roles = {
            "admin": {
                "description": "System administrator with full access",
                "permissions": [
                    f"{resource.value}:{action.value}"
                    for resource in ResourceType
                    for action in Action
                ],
            },
            "portfolio_manager": {
                "description": "Portfolio management access",
                "permissions": [
                    "portfolio:read",
                    "portfolio:update",
                    "portfolio:create",
                    "transaction:read",
                    "transaction:create",
                    "market_data:read",
                    "report:read",
                    "report:create",
                ],
            },
            "trader": {
                "description": "Trading operations access",
                "permissions": [
                    "transaction:read",
                    "transaction:create",
                    "market_data:read",
                    "portfolio:read",
                    "account:read",
                ],
            },
            "analyst": {
                "description": "Analysis and reporting access",
                "permissions": [
                    "market_data:read",
                    "report:read",
                    "report:create",
                    "portfolio:read",
                    "transaction:read",
                ],
            },
            "client": {
                "description": "Client access to own data",
                "permissions": [
                    "account:read",
                    "portfolio:read",
                    "transaction:read",
                    "report:read",
                ],
            },
            "compliance_officer": {
                "description": "Compliance monitoring access",
                "permissions": [
                    "transaction:read",
                    "account:read",
                    "portfolio:read",
                    "report:read",
                    "report:create",
                    "user:read",
                ],
            },
        }

    def authorize(self, request: AccessRequest) -> AuthorizationResult:
        """Authorize access request"""
        try:
            user_permissions = self._get_user_permissions(request.user_id)
            required_permission = f"{request.resource.value}:{request.action.value}"
            if required_permission not in user_permissions:
                return AuthorizationResult(
                    granted=False,
                    reason=f"Missing required permission: {required_permission}",
                    required_permissions=[required_permission],
                    user_permissions=user_permissions,
                    conditions_met=False,
                    risk_level="low",
                )
            resource_authorized = self._check_resource_authorization(
                request, user_permissions
            )
            if not resource_authorized.granted:
                return resource_authorized
            conditions_met = self._check_conditions(request, user_permissions)
            risk_level = self._assess_access_risk(request)
            return AuthorizationResult(
                granted=True,
                reason="Access granted",
                required_permissions=[required_permission],
                user_permissions=user_permissions,
                conditions_met=conditions_met,
                risk_level=risk_level,
            )
        except Exception as e:
            self.logger.error(f"Authorization error: {str(e)}", exc_info=True)
            return AuthorizationResult(
                granted=False,
                reason=f"Authorization system error: {str(e)}",
                required_permissions=[],
                user_permissions=[],
                conditions_met=False,
                risk_level="high",
            )

    def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for user"""
        try:
            cache_key = f"permissions:{user_id}"
            if (
                cache_key in self.permission_cache
                and cache_key in self.last_cache_update
                and (utc_now() - self.last_cache_update[cache_key] < self.cache_ttl)
            ):
                return self.permission_cache[cache_key]
            user_roles = (
                self.db.query(UserRole).filter(UserRole.user_id == user_id).all()
            )
            permissions = set()
            for user_role in user_roles:
                role_permissions = (
                    self.db.query(RolePermission)
                    .filter(RolePermission.role_id == user_role.role_id)
                    .all()
                )
                for role_permission in role_permissions:
                    permission = (
                        self.db.query(Permission)
                        .filter(Permission.id == role_permission.permission_id)
                        .first()
                    )
                    if permission:
                        permissions.add(f"{permission.resource}:{permission.action}")
            permissions_list = list(permissions)
            self.permission_cache[cache_key] = permissions_list
            self.last_cache_update[cache_key] = utc_now()
            return permissions_list
        except Exception as e:
            self.logger.error(f"Error getting user permissions: {str(e)}")
            return []

    def _check_resource_authorization(
        self, request: AccessRequest, user_permissions: List[str]
    ) -> AuthorizationResult:
        """Check resource-specific authorization rules"""
        try:
            if request.resource == ResourceType.ACCOUNT:
                if request.resource_id:
                    if not self._user_owns_resource(
                        request.user_id, "account", request.resource_id
                    ):
                        if "admin:read" not in user_permissions:
                            return AuthorizationResult(
                                granted=False,
                                reason="Access denied: Can only access own accounts",
                                required_permissions=[
                                    f"{request.resource.value}:{request.action.value}"
                                ],
                                user_permissions=user_permissions,
                                conditions_met=False,
                                risk_level="medium",
                            )
            elif request.resource == ResourceType.PORTFOLIO:
                if request.resource_id:
                    if not self._user_owns_resource(
                        request.user_id, "portfolio", request.resource_id
                    ):
                        if (
                            "admin:read" not in user_permissions
                            and "portfolio_manager"
                            not in self._get_user_roles(request.user_id)
                        ):
                            return AuthorizationResult(
                                granted=False,
                                reason="Access denied: Can only access assigned portfolios",
                                required_permissions=[
                                    f"{request.resource.value}:{request.action.value}"
                                ],
                                user_permissions=user_permissions,
                                conditions_met=False,
                                risk_level="medium",
                            )
            elif request.resource == ResourceType.TRANSACTION:
                if request.action in [Action.CREATE, Action.UPDATE, Action.DELETE]:
                    if not self._check_transaction_limits(request):
                        return AuthorizationResult(
                            granted=False,
                            reason="Transaction exceeds authorized limits",
                            required_permissions=[
                                f"{request.resource.value}:{request.action.value}"
                            ],
                            user_permissions=user_permissions,
                            conditions_met=False,
                            risk_level="high",
                        )
            elif request.resource == ResourceType.ADMIN:
                if "admin" not in self._get_user_roles(request.user_id):
                    return AuthorizationResult(
                        granted=False,
                        reason="Admin access required",
                        required_permissions=[
                            f"{request.resource.value}:{request.action.value}"
                        ],
                        user_permissions=user_permissions,
                        conditions_met=False,
                        risk_level="high",
                    )
            return AuthorizationResult(
                granted=True,
                reason="Resource authorization passed",
                required_permissions=[
                    f"{request.resource.value}:{request.action.value}"
                ],
                user_permissions=user_permissions,
                conditions_met=True,
                risk_level="low",
            )
        except Exception as e:
            self.logger.error(f"Resource authorization error: {str(e)}")
            return AuthorizationResult(
                granted=False,
                reason=f"Resource authorization error: {str(e)}",
                required_permissions=[],
                user_permissions=user_permissions,
                conditions_met=False,
                risk_level="high",
            )

    def _check_conditions(
        self, request: AccessRequest, user_permissions: List[str]
    ) -> bool:
        """Check context-based conditions"""
        try:
            if not request.context:
                return True
            if "time_restriction" in request.context:
                current_hour = utc_now().hour
                allowed_hours = request.context["time_restriction"]
                if current_hour not in allowed_hours:
                    return False
            if "ip_restriction" in request.context:
                allowed_ips = request.context["ip_restriction"]
                user_ip = request.context.get("user_ip")
                if user_ip and user_ip not in allowed_ips:
                    return False
            if (
                request.resource == ResourceType.TRANSACTION
                and "amount" in request.context
            ):
                amount = request.context["amount"]
                user_roles = self._get_user_roles(request.user_id)
                limits = {
                    "client": 10000,
                    "trader": 100000,
                    "portfolio_manager": 1000000,
                    "admin": float("inf"),
                }
                max_limit = 0
                for role in user_roles:
                    if role in limits:
                        max_limit = max(max_limit, limits[role])
                if amount > max_limit:
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Condition check error: {str(e)}")
            return False

    def _assess_access_risk(self, request: AccessRequest) -> str:
        """Assess risk level of access request"""
        risk_score = 0
        if request.action in [Action.DELETE, Action.EXECUTE]:
            risk_score += 3
        elif request.action in [Action.CREATE, Action.UPDATE]:
            risk_score += 2
        else:
            risk_score += 1
        if request.resource in [ResourceType.ADMIN, ResourceType.SYSTEM]:
            risk_score += 3
        elif request.resource in [ResourceType.TRANSACTION]:
            risk_score += 2
        if request.context:
            if request.context.get("amount", 0) > 100000:
                risk_score += 2
            if request.context.get("external_access", False):
                risk_score += 1
        if risk_score >= 6:
            return "high"
        elif risk_score >= 4:
            return "medium"
        else:
            return "low"

    def _user_owns_resource(
        self, user_id: str, resource_type: str, resource_id: str
    ) -> bool:
        """Check if user owns the resource"""
        try:
            if resource_type == "account":
                from app.models.models import Account

                account = (
                    self.db.query(Account)
                    .filter(Account.id == resource_id, Account.user_id == user_id)
                    .first()
                )
                return account is not None
            elif resource_type == "portfolio":
                from app.models.models import Portfolio

                portfolio = (
                    self.db.query(Portfolio)
                    .filter(Portfolio.id == resource_id, Portfolio.user_id == user_id)
                    .first()
                )
                return portfolio is not None
            return False
        except Exception as e:
            self.logger.error(f"Resource ownership check error: {str(e)}")
            return False

    def _get_user_roles(self, user_id: str) -> List[str]:
        """Get user roles"""
        try:
            user_roles = (
                self.db.query(UserRole).filter(UserRole.user_id == user_id).all()
            )
            roles = []
            for user_role in user_roles:
                role = self.db.query(Role).filter(Role.id == user_role.role_id).first()
                if role:
                    roles.append(role.name)
            return roles
        except Exception as e:
            self.logger.error(f"Error getting user roles: {str(e)}")
            return []

    def _check_transaction_limits(self, request: AccessRequest) -> bool:
        """Check transaction limits"""
        try:
            if not request.context or "amount" not in request.context:
                return True
            amount = request.context["amount"]
            user_roles = self._get_user_roles(request.user_id)
            daily_limits = {
                "client": 50000,
                "trader": 500000,
                "portfolio_manager": 5000000,
                "admin": float("inf"),
            }
            max_daily_limit = 0
            for role in user_roles:
                if role in daily_limits:
                    max_daily_limit = max(max_daily_limit, daily_limits[role])
            if amount > max_daily_limit:
                return False
            today = utc_now().date()
            from app.models.models import Transaction

            daily_total = (
                self.db.query(Transaction)
                .filter(
                    Transaction.user_id == request.user_id,
                    Transaction.created_at >= today,
                )
                .with_entities(Transaction.amount)
                .all()
            )
            current_daily_total = sum((t.amount for t in daily_total if t.amount))
            if current_daily_total + amount > max_daily_limit:
                return False
            return True
        except Exception as e:
            self.logger.error(f"Transaction limit check error: {str(e)}")
            return False

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign role to user"""
        try:
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if not role:
                self.logger.error(f"Role {role_name} not found")
                return False
            existing = (
                self.db.query(UserRole)
                .filter(UserRole.user_id == user_id, UserRole.role_id == role.id)
                .first()
            )
            if existing:
                return True
            user_role = UserRole(user_id=user_id, role_id=role.id)
            self.db.add(user_role)
            self.db.commit()
            self._clear_user_cache(user_id)
            self.logger.info(f"Assigned role {role_name} to user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Role assignment error: {str(e)}")
            self.db.rollback()
            return False

    def revoke_role(self, user_id: str, role_name: str) -> bool:
        """Revoke role from user"""
        try:
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if not role:
                return False
            user_role = (
                self.db.query(UserRole)
                .filter(UserRole.user_id == user_id, UserRole.role_id == role.id)
                .first()
            )
            if user_role:
                self.db.delete(user_role)
                self.db.commit()
                self._clear_user_cache(user_id)
                self.logger.info(f"Revoked role {role_name} from user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Role revocation error: {str(e)}")
            self.db.rollback()
            return False

    def create_role(
        self, role_name: str, description: str, permissions: List[str]
    ) -> bool:
        """Create new role with permissions"""
        try:
            existing_role = self.db.query(Role).filter(Role.name == role_name).first()
            if existing_role:
                return False
            role = Role(name=role_name, description=description)
            self.db.add(role)
            self.db.flush()
            for perm_string in permissions:
                resource, action = perm_string.split(":")
                permission = (
                    self.db.query(Permission)
                    .filter(
                        Permission.resource == resource, Permission.action == action
                    )
                    .first()
                )
                if not permission:
                    permission = Permission(resource=resource, action=action)
                    self.db.add(permission)
                    self.db.flush()
                role_permission = RolePermission(
                    role_id=role.id, permission_id=permission.id
                )
                self.db.add(role_permission)
            self.db.commit()
            self.logger.info(
                f"Created role {role_name} with {len(permissions)} permissions"
            )
            return True
        except Exception as e:
            self.logger.error(f"Role creation error: {str(e)}")
            self.db.rollback()
            return False

    def initialize_default_roles(self) -> bool:
        """Initialize default roles and permissions"""
        try:
            for role_name, role_config in self.default_roles.items():
                existing_role = (
                    self.db.query(Role).filter(Role.name == role_name).first()
                )
                if not existing_role:
                    self.create_role(
                        role_name,
                        role_config["description"],
                        role_config["permissions"],
                    )
            self.logger.info("Default roles initialized")
            return True
        except Exception as e:
            self.logger.error(f"Default role initialization error: {str(e)}")
            return False

    def _clear_user_cache(self, user_id: str) -> Any:
        """Clear user permission cache"""
        cache_key = f"permissions:{user_id}"
        if cache_key in self.permission_cache:
            del self.permission_cache[cache_key]
        if cache_key in self.last_cache_update:
            del self.last_cache_update[cache_key]

    def get_user_permissions_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user permissions"""
        try:
            roles = self._get_user_roles(user_id)
            permissions = self._get_user_permissions(user_id)
            permission_groups = {}
            for perm in permissions:
                resource, action = perm.split(":")
                if resource not in permission_groups:
                    permission_groups[resource] = []
                permission_groups[resource].append(action)
            return {
                "user_id": user_id,
                "roles": roles,
                "permissions": permissions,
                "permission_groups": permission_groups,
                "total_permissions": len(permissions),
            }
        except Exception as e:
            self.logger.error(f"Permission summary error: {str(e)}")
            return {}


def require_permission(resource: ResourceType, action: Action) -> Any:
    """Decorator to require specific permission for endpoint access"""

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: str) -> Any:
    """Decorator to require specific role for endpoint access"""

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


class AttributeBasedAccessControl:
    """Attribute-Based Access Control (ABAC) system for fine-grained permissions"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = logging.get_logger(__name__)

    def evaluate_policy(
        self,
        subject_attributes: Dict[str, Any],
        resource_attributes: Dict[str, Any],
        action_attributes: Dict[str, Any],
        environment_attributes: Dict[str, Any],
    ) -> bool:
        """Evaluate ABAC policy"""
        try:
            if "allowed_hours" in environment_attributes:
                current_hour = utc_now().hour
                if current_hour not in environment_attributes["allowed_hours"]:
                    return False
            if "allowed_locations" in environment_attributes:
                user_location = subject_attributes.get("location")
                if user_location not in environment_attributes["allowed_locations"]:
                    return False
            if resource_attributes.get("sensitivity") == "high":
                if subject_attributes.get("clearance_level", 0) < 3:
                    return False
            if "amount" in action_attributes:
                amount = action_attributes["amount"]
                max_amount = subject_attributes.get("max_transaction_amount", 0)
                if amount > max_amount:
                    return False
            return True
        except Exception as e:
            self.logger.error(f"ABAC policy evaluation error: {str(e)}")
            return False
