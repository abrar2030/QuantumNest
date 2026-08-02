"""Legacy Flask reimplementation of the API — NOT the live application.

The actual backend served in development and production is the FastAPI app
in ``app/main.py`` (started via ``run_flask.py``, which — despite its name —
launches ``app.main:app`` through uvicorn, not this module). This file isn't
imported by any entry point in the project. It's kept for reference but
receives no traffic; don't assume changes here affect the running API.
"""

import os
import traceback
from typing import Any

import redis
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.time_utils import utc_now
from app.db.flask_db import db
from app.middleware.security_middleware import SecurityConfig, SecurityMiddleware

# Conditional imports for services and AI modules
try:
    from app.ai.financial_advisor import AIFinancialAdvisor
    from app.ai.fraud_detection import AdvancedFraudDetectionSystem
    from app.ai.portfolio_optimization import PortfolioOptimizer

    AI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI modules not available: {e}")
    AIFinancialAdvisor = None
    AdvancedFraudDetectionSystem = None
    PortfolioOptimizer = None
    AI_AVAILABLE = False

try:
    from app.auth.authentication import AdvancedAuthenticationSystem
    from app.auth.authorization import RoleBasedAccessControl

    AUTH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Auth modules not available: {e}")
    AdvancedAuthenticationSystem = None
    RoleBasedAccessControl = None
    AUTH_AVAILABLE = False

try:
    from app.services.market_data_service import MarketDataService
    from app.services.risk_management_service import RiskManagementService
    from app.services.trading_service import TradingService

    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Service modules not available: {e}")
    MarketDataService = None
    RiskManagementService = None
    TradingService = None
    SERVICES_AVAILABLE = False
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import text
from werkzeug.exceptions import HTTPException


def create_app(config_name: Any = "development") -> Any:
    """Application factory pattern"""
    app = Flask(__name__)
    settings = get_settings()
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 20,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "max_overflow": 30,
    }
    setup_logging(app)
    logger = get_logger(__name__)
    db.init_app(app)
    Migrate(app, db)
    CORS(
        app,
        origins=settings.ALLOWED_ORIGINS,
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-API-Key",
            "X-Requested-With",
        ],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=True,
    )
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}")
        redis_client = None
    security_config = SecurityConfig(
        enable_rate_limiting=True,
        enable_request_signing=settings.ENABLE_REQUEST_SIGNING,
        enable_ip_filtering=settings.ENABLE_IP_FILTERING,
        enable_cors=True,
        enable_csrf_protection=settings.ENABLE_CSRF_PROTECTION,
        max_request_size=10 * 1024 * 1024,
    )
    SecurityMiddleware(app, security_config)
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
        # Initialize services conditionally
        if AUTH_AVAILABLE:
            app.auth_system = AdvancedAuthenticationSystem(db.session)
            app.rbac_system = RoleBasedAccessControl(db.session)
            logger.info("Auth systems initialized")
        else:
            app.auth_system = None
            app.rbac_system = None
            logger.warning("Auth systems not available")

        if SERVICES_AVAILABLE:
            app.trading_service = TradingService(db.session)
            app.market_data_service = MarketDataService()
            app.risk_management_service = RiskManagementService(db.session)
            logger.info("Trading services initialized")
        else:
            app.trading_service = None
            app.market_data_service = None
            app.risk_management_service = None
            logger.warning("Trading services not available")

        if AI_AVAILABLE:
            app.fraud_detection_system = AdvancedFraudDetectionSystem()
            app.ai_financial_advisor = AIFinancialAdvisor()
            app.portfolio_optimizer = PortfolioOptimizer()
            logger.info("AI systems initialized")
        else:
            app.fraud_detection_system = None
            app.ai_financial_advisor = None
            app.portfolio_optimizer = None
            logger.warning("AI systems not available")

        app.redis_client = redis_client

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP exception: {e.code} - {e.description}")
        return (
            jsonify({"error": e.name, "message": e.description, "status_code": e.code}),
            e.code,
        )

    @app.errorhandler(Exception)
    def handle_general_exception(e):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        if app.debug:
            return (
                jsonify(
                    {
                        "error": "Internal Server Error",
                        "message": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )
        else:
            return (
                jsonify(
                    {
                        "error": "Internal Server Error",
                        "message": "An unexpected error occurred",
                    }
                ),
                500,
            )

    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 errors"""
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found",
                }
            ),
            404,
        )

    @app.errorhandler(403)
    def handle_forbidden(e):
        """Handle 403 errors"""
        return (
            jsonify(
                {
                    "error": "Forbidden",
                    "message": "You do not have permission to access this resource",
                }
            ),
            403,
        )

    @app.errorhandler(401)
    def handle_unauthorized(e):
        """Handle 401 errors"""
        return (
            jsonify({"error": "Unauthorized", "message": "Authentication required"}),
            401,
        )

    @app.route("/health", methods=["GET"])
    def health_check():
        """Basic health check"""
        return jsonify(
            {
                "status": "healthy",
                "timestamp": utc_now().isoformat(),
                "version": "1.0.0",
            }
        )

    @app.route("/health/detailed", methods=["GET"])
    def detailed_health_check():
        """Detailed health check"""
        health_status = {
            "status": "healthy",
            "timestamp": utc_now().isoformat(),
            "version": "1.0.0",
            "components": {},
        }
        try:
            db.session.execute(text("SELECT 1"))
            health_status["components"]["database"] = "healthy"
        except Exception as e:
            health_status["components"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        try:
            if redis_client:
                redis_client.ping()
                health_status["components"]["redis"] = "healthy"
            else:
                health_status["components"]["redis"] = "not configured"
        except Exception as e:
            health_status["components"]["redis"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        try:
            if hasattr(app, "fraud_detection_system"):
                health_status["components"]["fraud_detection"] = "healthy"
            if hasattr(app, "ai_financial_advisor"):
                health_status["components"]["ai_advisor"] = "healthy"
            if hasattr(app, "portfolio_optimizer"):
                health_status["components"]["portfolio_optimizer"] = "healthy"
        except Exception as e:
            health_status["components"]["ai_services"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        return jsonify(health_status)

    @app.route("/", methods=["GET"])
    def root():
        """Root endpoint"""
        return jsonify(
            {
                "message": "Welcome to QuantumNest Capital API",
                "version": "1.0.0",
                "documentation": "/docs",
                "health": "/health",
            }
        )

    @app.route("/auth/login", methods=["POST"])
    def login():
        """User login endpoint"""
        try:
            data = request.get_json()
            if not data or not data.get("email") or (not data.get("password")):
                return (
                    jsonify(
                        {
                            "error": "Missing credentials",
                            "message": "Email and password are required",
                        }
                    ),
                    400,
                )
            device_fingerprint = request.headers.get("X-Device-Fingerprint", "unknown")
            ip_address = request.remote_addr
            user_agent = request.headers.get("User-Agent", "unknown")
            if not app.auth_system:
                return jsonify({"error": "Authentication not available"}), 503
            result = app.auth_system.authenticate_user_sync(
                email=data["email"],
                password=data["password"],
                device_fingerprint=device_fingerprint,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            if result.success:
                response_data = {
                    "success": True,
                    "access_token": result.access_token,
                    "refresh_token": result.refresh_token,
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user_id": result.user_id,
                }
                if result.requires_2fa:
                    response_data["requires_2fa"] = True
                    response_data["temp_session"] = result.session_token
                return jsonify(response_data)
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": result.error_message,
                            "requires_2fa": result.requires_2fa,
                            "temp_session": (
                                result.session_token if result.requires_2fa else None
                            ),
                        }
                    ),
                    401,
                )
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Authentication failed",
                        "message": "An error occurred during authentication",
                    }
                ),
                500,
            )

    @app.route("/auth/2fa/verify", methods=["POST"])
    def verify_2fa():
        """2FA verification endpoint"""
        try:
            data = request.get_json()
            required_fields = ["user_id", "temp_session", "totp_code"]
            if not all((field in data for field in required_fields)):
                return (
                    jsonify(
                        {
                            "error": "Missing required fields",
                            "message": "user_id, temp_session, and totp_code are required",
                        }
                    ),
                    400,
                )
            device_fingerprint = request.headers.get("X-Device-Fingerprint", "unknown")
            ip_address = request.remote_addr
            user_agent = request.headers.get("User-Agent", "unknown")
            if not app.auth_system:
                return jsonify({"error": "2FA verification not available"}), 503
            result = app.auth_system.verify_2fa_sync(
                user_id=data["user_id"],
                temp_session=data["temp_session"],
                totp_code=data["totp_code"],
                device_fingerprint=device_fingerprint,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            if result.success:
                return jsonify(
                    {
                        "success": True,
                        "access_token": result.access_token,
                        "refresh_token": result.refresh_token,
                        "token_type": "bearer",
                        "expires_in": 3600,
                        "user_id": result.user_id,
                    }
                )
            else:
                return (jsonify({"success": False, "error": result.error_message}), 401)
        except Exception as e:
            logger.error(f"2FA verification error: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "2FA verification failed",
                        "message": "An error occurred during 2FA verification",
                    }
                ),
                500,
            )

    @app.route("/auth/refresh", methods=["POST"])
    def refresh_token():
        """Token refresh endpoint"""
        try:
            data = request.get_json()
            if not data or not data.get("refresh_token"):
                return (
                    jsonify(
                        {
                            "error": "Missing refresh token",
                            "message": "Refresh token is required",
                        }
                    ),
                    400,
                )
            result = app.auth_system.refresh_access_token(data["refresh_token"])
            if result:
                return jsonify(result)
            else:
                return (
                    jsonify(
                        {
                            "error": "Invalid refresh token",
                            "message": "The refresh token is invalid or expired",
                        }
                    ),
                    401,
                )
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Token refresh failed",
                        "message": "An error occurred during token refresh",
                    }
                ),
                500,
            )

    @app.route("/auth/logout", methods=["POST"])
    def logout():
        """User logout endpoint"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return (
                    jsonify(
                        {
                            "error": "Missing authorization header",
                            "message": "Authorization header with Bearer token is required",
                        }
                    ),
                    401,
                )
            token = auth_header.split(" ")[1]
            token_data = app.auth_system.validate_token(token)
            if not token_data:
                return (
                    jsonify(
                        {
                            "error": "Invalid token",
                            "message": "The provided token is invalid",
                        }
                    ),
                    401,
                )
            success = app.auth_system.logout(token_data["session_id"])
            if success:
                return jsonify({"success": True, "message": "Successfully logged out"})
            else:
                return (
                    jsonify(
                        {
                            "error": "Logout failed",
                            "message": "An error occurred during logout",
                        }
                    ),
                    500,
                )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Logout failed",
                        "message": "An error occurred during logout",
                    }
                ),
                500,
            )

    @app.route("/market/quote/<symbol>", methods=["GET"])
    def get_quote(symbol):
        """Get real-time quote for a symbol"""
        try:
            quote = app.market_data_service.get_real_time_quote(symbol)
            if quote:
                return jsonify({"success": True, "data": quote})
            else:
                return (
                    jsonify(
                        {
                            "error": "Quote not found",
                            "message": f"No quote available for symbol {symbol}",
                        }
                    ),
                    404,
                )
        except Exception as e:
            logger.error(f"Quote retrieval error: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Quote retrieval failed",
                        "message": "An error occurred while retrieving the quote",
                    }
                ),
                500,
            )

    @app.route("/market/historical/<symbol>", methods=["GET"])
    def get_historical_data(symbol):
        """Get historical data for a symbol"""
        try:
            period = request.args.get("period", "1y")
            interval = request.args.get("interval", "1d")
            data = app.market_data_service.get_historical_data(symbol, period, interval)
            if data is not None and (not data.empty):
                data_json = data.reset_index().to_dict("records")
                return jsonify(
                    {
                        "success": True,
                        "data": data_json,
                        "symbol": symbol,
                        "period": period,
                        "interval": interval,
                    }
                )
            else:
                return (
                    jsonify(
                        {
                            "error": "Historical data not found",
                            "message": f"No historical data available for symbol {symbol}",
                        }
                    ),
                    404,
                )
        except Exception as e:
            logger.error(f"Historical data retrieval error: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Historical data retrieval failed",
                        "message": "An error occurred while retrieving historical data",
                    }
                ),
                500,
            )

    @app.route("/ai/risk-assessment", methods=["POST"])
    def assess_risk():
        """Assess risk for a transaction or portfolio"""
        try:
            data = request.get_json()
            if not data:
                return (
                    jsonify(
                        {"error": "Missing data", "message": "Request body is required"}
                    ),
                    400,
                )
            risk_assessment = app.risk_management_service.assess_transaction_risk(data)
            return jsonify({"success": True, "risk_assessment": risk_assessment})
        except Exception as e:
            logger.error(f"Risk assessment error: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Risk assessment failed",
                        "message": "An error occurred during risk assessment",
                    }
                ),
                500,
            )

    @app.route("/ai/fraud-detection", methods=["POST"])
    def detect_fraud():
        """Detect potential fraud in transaction"""
        try:
            data = request.get_json()
            if not data:
                return (
                    jsonify(
                        {
                            "error": "Missing data",
                            "message": "Transaction data is required",
                        }
                    ),
                    400,
                )
            fraud_result = app.fraud_detection_system.analyze_transaction(data)
            return jsonify({"success": True, "fraud_analysis": fraud_result})
        except Exception as e:
            logger.error(f"Fraud detection error: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Fraud detection failed",
                        "message": "An error occurred during fraud detection",
                    }
                ),
                500,
            )

    logger.info("QuantumNest Capital API initialized successfully")
    return app


app = create_app()
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_ENV") == "development",
    )
