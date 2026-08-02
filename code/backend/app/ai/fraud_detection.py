import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from app.core.time_utils import utc_now

warnings.filterwarnings("ignore")
import logging

import joblib
import networkx as nx
import tensorflow as tf
from sklearn.ensemble import (
    GradientBoostingClassifier,
    IsolationForest,
    RandomForestClassifier,
)
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import BatchNormalization, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class FraudType(str, Enum):
    ACCOUNT_TAKEOVER = "account_takeover"
    IDENTITY_THEFT = "identity_theft"
    PAYMENT_FRAUD = "payment_fraud"
    MONEY_LAUNDERING = "money_laundering"
    INSIDER_TRADING = "insider_trading"
    MARKET_MANIPULATION = "market_manipulation"
    PHISHING = "phishing"
    SYNTHETIC_IDENTITY = "synthetic_identity"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FraudAlert:
    """Fraud detection alert"""

    transaction_id: Optional[str]
    user_id: str
    fraud_type: FraudType
    risk_level: RiskLevel
    confidence_score: float
    risk_factors: List[str]
    recommended_actions: List[str]
    timestamp: datetime
    additional_context: Dict[str, Any]


@dataclass
class UserRiskProfile:
    """User risk profile for fraud detection"""

    user_id: str
    risk_score: float
    behavioral_patterns: Dict[str, Any]
    transaction_patterns: Dict[str, Any]
    device_patterns: Dict[str, Any]
    location_patterns: Dict[str, Any]
    network_connections: List[str]
    last_updated: datetime


class AdvancedFraudDetectionSystem:
    """Advanced fraud detection system with multiple ML models and rule engines"""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """Initialize fraud detection system"""
        self.config = {
            "models": [
                "random_forest",
                "gradient_boosting",
                "neural_network",
                "isolation_forest",
            ],
            "ensemble_method": "weighted_voting",
            "time_windows": [1, 7, 30, 90],
            "velocity_features": True,
            "network_features": True,
            "behavioral_features": True,
            "device_fingerprinting": True,
            "anomaly_threshold": 0.1,
            "isolation_forest_estimators": 100,
            "nn_epochs": 100,
            "nn_batch_size": 32,
            "nn_layers": [128, 64, 32],
            "nn_dropout": 0.3,
            "risk_thresholds": {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8,
                "critical": 0.95,
            },
            "monitoring_window": 300,
            "alert_cooldown": 3600,
            "max_network_depth": 3,
            "min_connection_strength": 0.1,
            "behavioral_window": 90,
            "pattern_deviation_threshold": 2.0,
        }
        if config:
            self.config.update(config)
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.user_profiles = {}
        self.alert_history = []
        self.is_trained = False

    def train_models(
        self, training_data: pd.DataFrame, target_column: str = "is_fraud"
    ) -> Dict[str, Any]:
        """Train fraud detection models"""
        try:
            logger.info("Training fraud detection models")
            features_df = self._engineer_features(training_data)
            self.feature_columns = [
                col for col in features_df.columns if col != target_column
            ]
            X = features_df[self.feature_columns]
            y = features_df[target_column]
            X = X.fillna(0)
            categorical_columns = X.select_dtypes(include=["object"]).columns
            for col in categorical_columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    X[col] = self.encoders[col].fit_transform(X[col].astype(str))
                else:
                    X[col] = self.encoders[col].transform(X[col].astype(str))
            self.scalers["standard"] = StandardScaler()
            X_scaled = self.scalers["standard"].fit_transform(X)
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, stratify=y
            )
            training_results = {}
            if "random_forest" in self.config["models"]:
                training_results["random_forest"] = self._train_random_forest(
                    X_train, y_train, X_test, y_test
                )
            if "gradient_boosting" in self.config["models"]:
                training_results["gradient_boosting"] = self._train_gradient_boosting(
                    X_train, y_train, X_test, y_test
                )
            if "neural_network" in self.config["models"]:
                training_results["neural_network"] = self._train_neural_network(
                    X_train, y_train, X_test, y_test
                )
            if "isolation_forest" in self.config["models"]:
                training_results["isolation_forest"] = self._train_isolation_forest(
                    X_train
                )
            self.is_trained = True
            logger.info("Fraud detection models trained successfully")
            return {
                "success": True,
                "results": training_results,
                "feature_columns": self.feature_columns,
            }
        except Exception as e:
            logger.error(
                f"Error training fraud detection models: {str(e)}", exc_info=True
            )
            return {"success": False, "error": str(e)}

    def predict_fraud(
        self,
        transaction_data: Dict[str, Any],
        user_data: Optional[Dict[str, Any]] = None,
    ) -> FraudAlert:
        """Predict fraud for a single transaction"""
        try:
            if not self.is_trained:
                raise ValueError("Models must be trained before making predictions")
            df = pd.DataFrame([transaction_data])
            if user_data:
                for key, value in user_data.items():
                    df[f"user_{key}"] = value
            features_df = self._engineer_features(df)
            X = features_df[self.feature_columns].fillna(0)
            for col in X.select_dtypes(include=["object"]).columns:
                if col in self.encoders:
                    X[col] = self.encoders[col].transform(X[col].astype(str))
                else:
                    X[col] = 0
            X_scaled = self.scalers["standard"].transform(X)
            predictions = {}
            probabilities = {}
            for model_name, model in self.models.items():
                if model_name == "isolation_forest":
                    pred = model.predict(X_scaled)[0]
                    predictions[model_name] = 1 if pred == -1 else 0
                    probabilities[model_name] = abs(
                        model.decision_function(X_scaled)[0]
                    )
                else:
                    predictions[model_name] = model.predict(X_scaled)[0]
                    if hasattr(model, "predict_proba"):
                        probabilities[model_name] = model.predict_proba(X_scaled)[0][1]
                    else:
                        probabilities[model_name] = predictions[model_name]
            if self.config["ensemble_method"] == "weighted_voting":
                weights = {
                    "random_forest": 0.3,
                    "gradient_boosting": 0.3,
                    "neural_network": 0.25,
                    "isolation_forest": 0.15,
                }
                ensemble_prob = sum(
                    (
                        weights.get(name, 0.25) * prob
                        for name, prob in probabilities.items()
                    )
                )
            else:
                ensemble_prob = np.mean(list(probabilities.values()))
            risk_level = self._get_risk_level(ensemble_prob)
            fraud_type = self._classify_fraud_type(transaction_data, ensemble_prob)
            risk_factors = self._identify_risk_factors(
                transaction_data, user_data, predictions
            )
            recommendations = self._generate_recommendations(
                risk_level, fraud_type, risk_factors
            )
            alert = FraudAlert(
                transaction_id=transaction_data.get("transaction_id"),
                user_id=transaction_data.get("user_id", "unknown"),
                fraud_type=fraud_type,
                risk_level=risk_level,
                confidence_score=float(ensemble_prob),
                risk_factors=risk_factors,
                recommended_actions=recommendations,
                timestamp=utc_now(),
                additional_context={
                    "model_predictions": predictions,
                    "model_probabilities": probabilities,
                    "ensemble_probability": float(ensemble_prob),
                },
            )
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                self.alert_history.append(alert)
            return alert
        except Exception as e:
            logger.error(f"Error predicting fraud: {str(e)}", exc_info=True)
            return FraudAlert(
                transaction_id=transaction_data.get("transaction_id"),
                user_id=transaction_data.get("user_id", "unknown"),
                fraud_type=FraudType.PAYMENT_FRAUD,
                risk_level=RiskLevel.MEDIUM,
                confidence_score=0.5,
                risk_factors=["System error during fraud detection"],
                recommended_actions=["Manual review required"],
                timestamp=utc_now(),
                additional_context={"error": str(e)},
            )

    def update_user_profile(
        self,
        user_id: str,
        transaction_data: Dict[str, Any],
        device_data: Optional[Dict[str, Any]] = None,
        location_data: Optional[Dict[str, Any]] = None,
    ) -> UserRiskProfile:
        """Update user risk profile with new transaction data"""
        try:
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
            else:
                profile = UserRiskProfile(
                    user_id=user_id,
                    risk_score=0.5,
                    behavioral_patterns={},
                    transaction_patterns={},
                    device_patterns={},
                    location_patterns={},
                    network_connections=[],
                    last_updated=utc_now(),
                )
            self._update_transaction_patterns(profile, transaction_data)
            if device_data:
                self._update_device_patterns(profile, device_data)
            if location_data:
                self._update_location_patterns(profile, location_data)
            profile.risk_score = self._calculate_user_risk_score(profile)
            profile.last_updated = utc_now()
            self.user_profiles[user_id] = profile
            return profile
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return self.user_profiles.get(
                user_id,
                UserRiskProfile(
                    user_id=user_id,
                    risk_score=0.5,
                    behavioral_patterns={},
                    transaction_patterns={},
                    device_patterns={},
                    location_patterns={},
                    network_connections=[],
                    last_updated=utc_now(),
                ),
            )

    def analyze_transaction_network(
        self, transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze transaction network for suspicious patterns"""
        try:
            G = nx.Graph()
            for transaction in transactions:
                sender = transaction.get("sender_id")
                receiver = transaction.get("receiver_id")
                amount = transaction.get("amount", 0)
                if sender and receiver:
                    if G.has_edge(sender, receiver):
                        G[sender][receiver]["weight"] += amount
                        G[sender][receiver]["count"] += 1
                    else:
                        G.add_edge(sender, receiver, weight=amount, count=1)
            analysis = {
                "network_stats": {
                    "nodes": G.number_of_nodes(),
                    "edges": G.number_of_edges(),
                    "density": nx.density(G),
                    "connected_components": nx.number_connected_components(G),
                },
                "suspicious_patterns": [],
                "high_risk_nodes": [],
                "unusual_connections": [],
            }
            cycles = list(nx.simple_cycles(G.to_directed()))
            if cycles:
                analysis["suspicious_patterns"].append(
                    {
                        "type": "circular_transactions",
                        "count": len(cycles),
                        "cycles": cycles[:10],
                    }
                )
            degrees = dict(G.degree())
            high_degree_threshold = np.percentile(list(degrees.values()), 95)
            high_degree_nodes = [
                node
                for node, degree in degrees.items()
                if degree > high_degree_threshold
            ]
            if high_degree_nodes:
                analysis["high_risk_nodes"] = high_degree_nodes
            edge_weights = [data["weight"] for _, _, data in G.edges(data=True)]
            if edge_weights:
                weight_threshold = np.percentile(edge_weights, 95)
                unusual_edges = [
                    (u, v, data)
                    for u, v, data in G.edges(data=True)
                    if data["weight"] > weight_threshold
                ]
                analysis["unusual_connections"] = [
                    {"sender": u, "receiver": v, "amount": data["weight"]}
                    for u, v, data in unusual_edges[:10]
                ]
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing transaction network: {str(e)}")
            return {"error": str(e)}

    def detect_account_takeover(
        self, user_id: str, session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect potential account takeover"""
        try:
            if user_id not in self.user_profiles:
                return {"risk_level": "medium", "reason": "No user profile available"}
            profile = self.user_profiles[user_id]
            risk_factors = []
            risk_score = 0.0
            current_device = session_data.get("device_fingerprint")
            if current_device and current_device not in profile.device_patterns:
                risk_factors.append("Unknown device")
                risk_score += 0.3
            current_location = session_data.get("location")
            if current_location:
                known_locations = profile.location_patterns.get(
                    "frequent_locations", []
                )
                if not any(
                    (
                        self._calculate_distance(current_location, loc) < 100
                        for loc in known_locations
                    )
                ):
                    risk_factors.append("Unusual location")
                    risk_score += 0.4
            current_time = utc_now().hour
            typical_hours = profile.behavioral_patterns.get("login_hours", [])
            if typical_hours and current_time not in typical_hours:
                risk_factors.append("Unusual login time")
                risk_score += 0.2
            session_duration = session_data.get("session_duration", 0)
            typical_duration = profile.behavioral_patterns.get(
                "avg_session_duration", 1800
            )
            if abs(session_duration - typical_duration) > typical_duration * 2:
                risk_factors.append("Unusual session duration")
                risk_score += 0.1
            if risk_score >= 0.8:
                risk_level = "critical"
            elif risk_score >= 0.6:
                risk_level = "high"
            elif risk_score >= 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
            return {
                "risk_level": risk_level,
                "risk_score": float(risk_score),
                "risk_factors": risk_factors,
                "recommended_actions": self._get_takeover_recommendations(risk_level),
            }
        except Exception as e:
            logger.error(f"Error detecting account takeover: {str(e)}")
            return {"risk_level": "medium", "error": str(e)}

    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for fraud detection"""
        df = data.copy()
        if "amount" in df.columns:
            df["amount_log"] = np.log1p(df["amount"])
            df["amount_rounded"] = (df["amount"] % 1 == 0).astype(int)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["hour"] = df["timestamp"].dt.hour
            df["day_of_week"] = df["timestamp"].dt.dayofweek
            df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
            df["is_night"] = ((df["hour"] < 6) | (df["hour"] > 22)).astype(int)
        if "user_id" in df.columns and len(df) > 1:
            df = self._add_velocity_features(df)
        if "device_fingerprint" in df.columns:
            df["device_risk_score"] = df["device_fingerprint"].apply(
                self._calculate_device_risk
            )
        if "ip_address" in df.columns:
            df["ip_risk_score"] = df["ip_address"].apply(self._calculate_ip_risk)
        if "merchant_category" in df.columns:
            high_risk_categories = [
                "gambling",
                "adult",
                "cryptocurrency",
                "money_transfer",
            ]
            df["high_risk_merchant"] = (
                df["merchant_category"].isin(high_risk_categories).astype(int)
            )
        return df

    def _add_velocity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add velocity-based features"""
        if "user_id" not in df.columns or "timestamp" not in df.columns:
            return df
        df = df.sort_values(["user_id", "timestamp"])
        for window in self.config["time_windows"]:
            window_str = f"{window}D"
            df[f"tx_count_{window}d"] = (
                df.groupby("user_id")["timestamp"]
                .rolling(window_str, on="timestamp")
                .count()
                .reset_index(level=0, drop=True)
            )
            if "amount" in df.columns:
                df[f"tx_amount_{window}d"] = (
                    df.groupby("user_id")["amount"]
                    .rolling(window_str, on="timestamp")
                    .sum()
                    .reset_index(level=0, drop=True)
                )
        return df

    def _train_random_forest(
        self, X_train: Any, y_train: Any, X_test: Any, y_test: Any
    ) -> Dict[str, Any]:
        """Train Random Forest model"""
        try:
            model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, class_weight="balanced"
            )
            model.fit(X_train, y_train)
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            if hasattr(model, "predict_proba"):
                y_pred_proba = model.predict_proba(X_test)[:, 1]
                auc_score = roc_auc_score(y_test, y_pred_proba)
            else:
                auc_score = None
            self.models["random_forest"] = model
            return {
                "success": True,
                "train_accuracy": float(train_score),
                "test_accuracy": float(test_score),
                "auc_score": float(auc_score) if auc_score else None,
                "feature_importance": dict(
                    zip(self.feature_columns, model.feature_importances_, strict=False)
                ),
            }
        except Exception as e:
            logger.error(f"Error training Random Forest: {str(e)}")
            return {"success": False, "error": str(e)}

    def _train_gradient_boosting(
        self, X_train: Any, y_train: Any, X_test: Any, y_test: Any
    ) -> Dict[str, Any]:
        """Train Gradient Boosting model"""
        try:
            model = GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42
            )
            model.fit(X_train, y_train)
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            auc_score = roc_auc_score(y_test, y_pred_proba)
            self.models["gradient_boosting"] = model
            return {
                "success": True,
                "train_accuracy": float(train_score),
                "test_accuracy": float(test_score),
                "auc_score": float(auc_score),
                "feature_importance": dict(
                    zip(self.feature_columns, model.feature_importances_, strict=False)
                ),
            }
        except Exception as e:
            logger.error(f"Error training Gradient Boosting: {str(e)}")
            return {"success": False, "error": str(e)}

    def _train_neural_network(
        self, X_train: Any, y_train: Any, X_test: Any, y_test: Any
    ) -> Dict[str, Any]:
        """Train Neural Network model"""
        try:
            model = Sequential()
            model.add(
                Dense(
                    self.config["nn_layers"][0],
                    activation="relu",
                    input_shape=(X_train.shape[1],),
                )
            )
            model.add(BatchNormalization())
            model.add(Dropout(self.config["nn_dropout"]))
            for units in self.config["nn_layers"][1:]:
                model.add(Dense(units, activation="relu"))
                model.add(BatchNormalization())
                model.add(Dropout(self.config["nn_dropout"]))
            model.add(Dense(1, activation="sigmoid"))
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss="binary_crossentropy",
                metrics=["accuracy"],
            )
            early_stopping = EarlyStopping(
                monitor="val_loss", patience=10, restore_best_weights=True
            )
            model.fit(
                X_train,
                y_train,
                validation_data=(X_test, y_test),
                epochs=self.config["nn_epochs"],
                batch_size=self.config["nn_batch_size"],
                callbacks=[early_stopping],
                verbose=0,
            )
            train_loss, train_acc = model.evaluate(X_train, y_train, verbose=0)
            test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
            y_pred_proba = model.predict(X_test, verbose=0).flatten()
            auc_score = roc_auc_score(y_test, y_pred_proba)
            self.models["neural_network"] = model
            return {
                "success": True,
                "train_accuracy": float(train_acc),
                "test_accuracy": float(test_acc),
                "auc_score": float(auc_score),
                "final_loss": float(test_loss),
            }
        except Exception as e:
            logger.error(f"Error training Neural Network: {str(e)}")
            return {"success": False, "error": str(e)}

    def _train_isolation_forest(self, X_train: Any) -> Dict[str, Any]:
        """Train Isolation Forest for anomaly detection"""
        try:
            model = IsolationForest(
                contamination=self.config["anomaly_threshold"],
                n_estimators=self.config["isolation_forest_estimators"],
                random_state=42,
            )
            model.fit(X_train)
            anomaly_scores = model.decision_function(X_train)
            predictions = model.predict(X_train)
            anomaly_rate = np.sum(predictions == -1) / len(predictions)
            self.models["isolation_forest"] = model
            return {
                "success": True,
                "anomaly_rate": float(anomaly_rate),
                "mean_anomaly_score": float(np.mean(anomaly_scores)),
            }
        except Exception as e:
            logger.error(f"Error training Isolation Forest: {str(e)}")
            return {"success": False, "error": str(e)}

    def _get_risk_level(self, probability: float) -> RiskLevel:
        """Convert probability to risk level"""
        thresholds = self.config["risk_thresholds"]
        if probability >= thresholds["critical"]:
            return RiskLevel.CRITICAL
        elif probability >= thresholds["high"]:
            return RiskLevel.HIGH
        elif probability >= thresholds["medium"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _classify_fraud_type(
        self, transaction_data: Dict[str, Any], probability: float
    ) -> FraudType:
        """Classify the type of fraud based on transaction characteristics"""
        amount = transaction_data.get("amount", 0)
        merchant_category = transaction_data.get("merchant_category", "")
        if amount > 10000:
            return FraudType.MONEY_LAUNDERING
        elif merchant_category in ["gambling", "adult"]:
            return FraudType.PAYMENT_FRAUD
        elif probability > 0.9:
            return FraudType.IDENTITY_THEFT
        else:
            return FraudType.PAYMENT_FRAUD

    def _identify_risk_factors(
        self,
        transaction_data: Dict[str, Any],
        user_data: Optional[Dict[str, Any]],
        predictions: Dict[str, Any],
    ) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []
        flagging_models = [name for name, pred in predictions.items() if pred == 1]
        if flagging_models:
            risk_factors.append(f"Flagged by models: {', '.join(flagging_models)}")
        amount = transaction_data.get("amount", 0)
        if amount > 5000:
            risk_factors.append("High transaction amount")
        elif amount < 1:
            risk_factors.append("Unusually low amount")
        timestamp = transaction_data.get("timestamp")
        if timestamp:
            hour = pd.to_datetime(timestamp).hour
            if hour < 6 or hour > 22:
                risk_factors.append("Transaction during unusual hours")
        if user_data and "location" in transaction_data:
            pass
        return risk_factors

    def _generate_recommendations(
        self, risk_level: RiskLevel, fraud_type: FraudType, risk_factors: List[str]
    ) -> List[str]:
        """Generate recommended actions based on risk assessment"""
        recommendations = []
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend(
                [
                    "Block transaction immediately",
                    "Freeze account pending investigation",
                    "Contact user via verified phone number",
                    "Escalate to fraud investigation team",
                ]
            )
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend(
                [
                    "Hold transaction for manual review",
                    "Request additional authentication",
                    "Monitor account for 24 hours",
                    "Flag for enhanced monitoring",
                ]
            )
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend(
                [
                    "Apply additional verification",
                    "Monitor for related transactions",
                    "Log for pattern analysis",
                ]
            )
        else:
            recommendations.append("Allow transaction with standard monitoring")
        if fraud_type == FraudType.ACCOUNT_TAKEOVER:
            recommendations.append("Force password reset")
        elif fraud_type == FraudType.MONEY_LAUNDERING:
            recommendations.append("Report to financial intelligence unit")
        return recommendations

    def _update_transaction_patterns(
        self, profile: UserRiskProfile, transaction_data: Dict[str, Any]
    ) -> Any:
        """Update user transaction patterns"""
        amount = transaction_data.get("amount", 0)
        if "amounts" not in profile.transaction_patterns:
            profile.transaction_patterns["amounts"] = []
        profile.transaction_patterns["amounts"].append(amount)
        if len(profile.transaction_patterns["amounts"]) > 100:
            profile.transaction_patterns["amounts"] = profile.transaction_patterns[
                "amounts"
            ][-100:]
        timestamp = transaction_data.get("timestamp")
        if timestamp:
            hour = pd.to_datetime(timestamp).hour
            if "hours" not in profile.transaction_patterns:
                profile.transaction_patterns["hours"] = []
            profile.transaction_patterns["hours"].append(hour)
        merchant_category = transaction_data.get("merchant_category")
        if merchant_category:
            if "merchant_categories" not in profile.transaction_patterns:
                profile.transaction_patterns["merchant_categories"] = {}
            if merchant_category in profile.transaction_patterns["merchant_categories"]:
                profile.transaction_patterns["merchant_categories"][
                    merchant_category
                ] += 1
            else:
                profile.transaction_patterns["merchant_categories"][
                    merchant_category
                ] = 1

    def _update_device_patterns(
        self, profile: UserRiskProfile, device_data: Dict[str, Any]
    ) -> Any:
        """Update user device patterns"""
        device_fingerprint = device_data.get("device_fingerprint")
        if device_fingerprint:
            if "devices" not in profile.device_patterns:
                profile.device_patterns["devices"] = {}
            if device_fingerprint in profile.device_patterns["devices"]:
                profile.device_patterns["devices"][device_fingerprint] += 1
            else:
                profile.device_patterns["devices"][device_fingerprint] = 1

    def _update_location_patterns(
        self, profile: UserRiskProfile, location_data: Dict[str, Any]
    ) -> Any:
        """Update user location patterns"""
        location = location_data.get("location")
        if location:
            if "locations" not in profile.location_patterns:
                profile.location_patterns["locations"] = {}
            location_key = f"{location.get('lat', 0):.2f},{location.get('lon', 0):.2f}"
            if location_key in profile.location_patterns["locations"]:
                profile.location_patterns["locations"][location_key] += 1
            else:
                profile.location_patterns["locations"][location_key] = 1

    def _calculate_user_risk_score(self, profile: UserRiskProfile) -> float:
        """Calculate overall risk score for user"""
        risk_score = 0.5
        device_count = len(profile.device_patterns.get("devices", {}))
        if device_count > 5:
            risk_score += 0.1
        location_count = len(profile.location_patterns.get("locations", {}))
        if location_count > 10:
            risk_score += 0.1
        amounts = profile.transaction_patterns.get("amounts", [])
        if amounts:
            amount_cv = (
                np.std(amounts) / np.mean(amounts) if np.mean(amounts) > 0 else 0
            )
            if amount_cv > 2.0:
                risk_score += 0.2
        return min(risk_score, 1.0)

    def _calculate_device_risk(self, device_fingerprint: str) -> float:
        """Calculate risk score for device"""
        return 0.1

    def _calculate_ip_risk(self, ip_address: str) -> float:
        """Calculate risk score for IP address"""
        return 0.1

    def _calculate_distance(
        self, loc1: Dict[str, float], loc2: Dict[str, float]
    ) -> float:
        """Calculate distance between two locations in km"""
        from math import asin, cos, radians, sin, sqrt

        lat1, lon1 = (radians(loc1["lat"]), radians(loc1["lon"]))
        lat2, lon2 = (radians(loc2["lat"]), radians(loc2["lon"]))
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371
        return c * r

    def _get_takeover_recommendations(self, risk_level: str) -> List[str]:
        """Get recommendations for account takeover scenarios"""
        if risk_level == "critical":
            return [
                "Lock account immediately",
                "Force password reset",
                "Require identity verification",
                "Contact user via verified channels",
            ]
        elif risk_level == "high":
            return [
                "Require additional authentication",
                "Send security alert to user",
                "Monitor session closely",
            ]
        elif risk_level == "medium":
            return ["Prompt for additional verification", "Log security event"]
        else:
            return ["Continue with standard monitoring"]

    def save_models(self, filepath: str) -> bool:
        """Save trained models"""
        try:
            import os

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            sklearn_models = {}
            for name, model in self.models.items():
                if name in ["random_forest", "gradient_boosting", "isolation_forest"]:
                    sklearn_models[name] = model
            if sklearn_models:
                joblib.dump(sklearn_models, f"{filepath}_sklearn.pkl")
            if "neural_network" in self.models:
                self.models["neural_network"].save(f"{filepath}_neural_network.h5")
            joblib.dump(self.scalers, f"{filepath}_scalers.pkl")
            joblib.dump(self.encoders, f"{filepath}_encoders.pkl")
            joblib.dump(self.config, f"{filepath}_config.pkl")
            joblib.dump(self.feature_columns, f"{filepath}_features.pkl")
            logger.info(f"Fraud detection models saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False

    def load_models(self, filepath: str) -> bool:
        """Load trained models"""
        try:
            self.config = joblib.load(f"{filepath}_config.pkl")
            self.feature_columns = joblib.load(f"{filepath}_features.pkl")
            self.scalers = joblib.load(f"{filepath}_scalers.pkl")
            self.encoders = joblib.load(f"{filepath}_encoders.pkl")
            try:
                sklearn_models = joblib.load(f"{filepath}_sklearn.pkl")
                self.models.update(sklearn_models)
            except FileNotFoundError:
                pass
            try:
                self.models["neural_network"] = tf.keras.models.load_model(
                    f"{filepath}_neural_network.h5"
                )
            except FileNotFoundError:
                pass
            self.is_trained = True
            logger.info(f"Fraud detection models loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False
