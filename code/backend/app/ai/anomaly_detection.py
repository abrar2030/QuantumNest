import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
import logging

import joblib
import tensorflow as tf
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.svm import OneClassSVM
from statsmodels.tsa.seasonal import seasonal_decompose
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AnomalyType(str, Enum):
    POINT_ANOMALY = "point_anomaly"
    CONTEXTUAL_ANOMALY = "contextual_anomaly"
    COLLECTIVE_ANOMALY = "collective_anomaly"


class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyResult:
    """Anomaly detection result"""

    timestamp: datetime
    value: float
    anomaly_score: float
    is_anomaly: bool
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    confidence: float
    explanation: str
    context: Dict[str, Any]


class FinancialAnomalyDetector:
    """Advanced anomaly detection system for financial data"""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """Initialize anomaly detector"""
        self.config = {
            "methods": [
                "isolation_forest",
                "autoencoder",
                "statistical",
                "lstm_autoencoder",
            ],
            "ensemble_method": "voting",
            "statistical_threshold": 3.0,
            "seasonal_period": 252,
            "rolling_window": 30,
            "isolation_contamination": 0.1,
            "isolation_n_estimators": 100,
            "autoencoder_threshold": 0.95,
            "autoencoder_epochs": 50,
            "autoencoder_batch_size": 32,
            "lstm_sequence_length": 30,
            "lstm_encoding_dim": 10,
            "lstm_epochs": 50,
            "context_features": ["volume", "volatility", "market_cap", "sector"],
            "severity_thresholds": {
                "low": 0.6,
                "medium": 0.75,
                "high": 0.9,
                "critical": 0.95,
            },
        }
        if config:
            self.config.update(config)
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        self.feature_columns = []

    def fit(self, data: pd.DataFrame, target_column: str = "close") -> Dict[str, Any]:
        """Train anomaly detection models"""
        try:
            logger.info("Training anomaly detection models")
            features_df = self._prepare_features(data, target_column)
            self.feature_columns = features_df.columns.tolist()
            self.scalers["standard"] = StandardScaler()
            self.scalers["robust"] = RobustScaler()
            features_standard = self.scalers["standard"].fit_transform(features_df)
            features_robust = self.scalers["robust"].fit_transform(features_df)
            results = {}
            if "isolation_forest" in self.config["methods"]:
                results["isolation_forest"] = self._train_isolation_forest(
                    features_standard
                )
            if "autoencoder" in self.config["methods"]:
                results["autoencoder"] = self._train_autoencoder(features_standard)
            if "lstm_autoencoder" in self.config["methods"]:
                results["lstm_autoencoder"] = self._train_lstm_autoencoder(
                    data, target_column
                )
            if "one_class_svm" in self.config["methods"]:
                results["one_class_svm"] = self._train_one_class_svm(features_robust)
            if "statistical" in self.config["methods"]:
                results["statistical"] = {
                    "success": True,
                    "message": "Statistical method ready",
                }
            self.is_trained = True
            logger.info("Anomaly detection models trained successfully")
            return {
                "success": True,
                "results": results,
                "feature_columns": self.feature_columns,
            }
        except Exception as e:
            logger.error(
                f"Error training anomaly detection models: {str(e)}", exc_info=True
            )
            return {"success": False, "error": str(e)}

    def detect_anomalies(
        self, data: pd.DataFrame, target_column: str = "close"
    ) -> List[AnomalyResult]:
        """Detect anomalies in data"""
        try:
            if not self.is_trained:
                raise ValueError("Models must be trained before detecting anomalies")
            logger.info("Detecting anomalies in data")
            features_df = self._prepare_features(data, target_column)
            features_standard = self.scalers["standard"].transform(features_df)
            features_robust = self.scalers["robust"].transform(features_df)
            method_results = {}
            if (
                "isolation_forest" in self.config["methods"]
                and "isolation_forest" in self.models
            ):
                method_results["isolation_forest"] = self._detect_isolation_forest(
                    features_standard
                )
            if "autoencoder" in self.config["methods"] and "autoencoder" in self.models:
                method_results["autoencoder"] = self._detect_autoencoder(
                    features_standard
                )
            if (
                "lstm_autoencoder" in self.config["methods"]
                and "lstm_autoencoder" in self.models
            ):
                method_results["lstm_autoencoder"] = self._detect_lstm_autoencoder(
                    data, target_column
                )
            if (
                "one_class_svm" in self.config["methods"]
                and "one_class_svm" in self.models
            ):
                method_results["one_class_svm"] = self._detect_one_class_svm(
                    features_robust
                )
            if "statistical" in self.config["methods"]:
                method_results["statistical"] = self._detect_statistical(
                    data, target_column
                )
            anomalies = self._combine_results(method_results, data, target_column)
            logger.info(
                f"Detected {len([a for a in anomalies if a.is_anomaly])} anomalies"
            )
            return anomalies
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}", exc_info=True)
            return []

    def _prepare_features(self, data: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Prepare features for anomaly detection"""
        df = data.copy()
        features = pd.DataFrame(index=df.index)
        features["price"] = df[target_column]
        features["returns"] = df[target_column].pct_change()
        features["log_returns"] = np.log(df[target_column] / df[target_column].shift(1))
        features["volatility_5"] = features["returns"].rolling(5).std()
        features["volatility_20"] = features["returns"].rolling(20).std()
        features["volatility_ratio"] = (
            features["volatility_5"] / features["volatility_20"]
        )
        if "volume" in df.columns:
            features["volume"] = df["volume"]
            features["volume_ma"] = df["volume"].rolling(20).mean()
            features["volume_ratio"] = df["volume"] / features["volume_ma"]
            features["price_volume"] = features["price"] * features["volume"]
        features["sma_5"] = df[target_column].rolling(5).mean()
        features["sma_20"] = df[target_column].rolling(20).mean()
        features["price_sma_ratio"] = features["price"] / features["sma_20"]
        features["momentum_5"] = df[target_column].pct_change(5)
        features["momentum_10"] = df[target_column].pct_change(10)
        if all((col in df.columns for col in ["high", "low"])):
            features["daily_range"] = (df["high"] - df["low"]) / df[target_column]
            features["true_range"] = np.maximum(
                df["high"] - df["low"],
                np.maximum(
                    abs(df["high"] - df[target_column].shift(1)),
                    abs(df["low"] - df[target_column].shift(1)),
                ),
            )
        if hasattr(df.index, "dayofweek"):
            features["day_of_week"] = df.index.dayofweek
            features["month"] = df.index.month
            features["quarter"] = df.index.quarter
        features["z_score"] = (
            features["price"] - features["price"].rolling(20).mean()
        ) / features["price"].rolling(20).std()
        features["percentile_rank"] = features["price"].rolling(50).rank(pct=True)
        for lag in [1, 2, 3, 5]:
            features[f"returns_lag_{lag}"] = features["returns"].shift(lag)
            features[f"volatility_lag_{lag}"] = features["volatility_20"].shift(lag)
        return features.dropna()

    def _train_isolation_forest(self, features: np.ndarray) -> Dict[str, Any]:
        """Train Isolation Forest model"""
        try:
            model = IsolationForest(
                contamination=self.config["isolation_contamination"],
                n_estimators=self.config["isolation_n_estimators"],
                random_state=42,
            )
            model.fit(features)
            self.models["isolation_forest"] = model
            return {"success": True, "message": "Isolation Forest trained successfully"}
        except Exception as e:
            logger.error(f"Error training Isolation Forest: {str(e)}")
            return {"success": False, "error": str(e)}

    def _train_autoencoder(self, features: np.ndarray) -> Dict[str, Any]:
        """Train autoencoder model"""
        try:
            input_dim = features.shape[1]
            encoding_dim = max(input_dim // 4, 5)
            input_layer = Input(shape=(input_dim,))
            encoded = Dense(encoding_dim * 2, activation="relu")(input_layer)
            encoded = Dropout(0.2)(encoded)
            encoded = Dense(encoding_dim, activation="relu")(encoded)
            decoded = Dense(encoding_dim * 2, activation="relu")(encoded)
            decoded = Dropout(0.2)(decoded)
            decoded = Dense(input_dim, activation="linear")(decoded)
            autoencoder = Model(input_layer, decoded)
            autoencoder.compile(optimizer=Adam(0.001), loss="mse")
            history = autoencoder.fit(
                features,
                features,
                epochs=self.config["autoencoder_epochs"],
                batch_size=self.config["autoencoder_batch_size"],
                validation_split=0.2,
                verbose=0,
            )
            reconstructions = autoencoder.predict(features, verbose=0)
            reconstruction_errors = np.mean(
                np.square(features - reconstructions), axis=1
            )
            threshold = np.percentile(
                reconstruction_errors, self.config["autoencoder_threshold"] * 100
            )
            self.models["autoencoder"] = {"model": autoencoder, "threshold": threshold}
            return {
                "success": True,
                "message": "Autoencoder trained successfully",
                "final_loss": history.history["loss"][-1],
                "threshold": threshold,
            }
        except Exception as e:
            logger.error(f"Error training autoencoder: {str(e)}")
            return {"success": False, "error": str(e)}

    def _train_lstm_autoencoder(
        self, data: pd.DataFrame, target_column: str
    ) -> Dict[str, Any]:
        """Train LSTM autoencoder for sequence anomalies"""
        try:
            sequences = self._create_sequences(
                data[target_column].values, self.config["lstm_sequence_length"]
            )
            if len(sequences) == 0:
                return {"success": False, "error": "Not enough data for LSTM sequences"}
            scaler = StandardScaler()
            sequences_scaled = scaler.fit_transform(sequences.reshape(-1, 1)).reshape(
                sequences.shape
            )
            self.scalers["lstm"] = scaler
            input_dim = sequences.shape[1]
            encoding_dim = self.config["lstm_encoding_dim"]
            model = Sequential(
                [
                    LSTM(
                        encoding_dim * 2,
                        activation="relu",
                        input_shape=(input_dim, 1),
                        return_sequences=True,
                    ),
                    LSTM(encoding_dim, activation="relu", return_sequences=False),
                    Dense(encoding_dim, activation="relu"),
                    Dense(encoding_dim * 2, activation="relu"),
                    Dense(input_dim, activation="linear"),
                ]
            )
            model.compile(optimizer=Adam(0.001), loss="mse")
            X = sequences_scaled.reshape(
                sequences_scaled.shape[0], sequences_scaled.shape[1], 1
            )
            y = sequences_scaled
            history = model.fit(
                X,
                y,
                epochs=self.config["lstm_epochs"],
                batch_size=32,
                validation_split=0.2,
                verbose=0,
            )
            predictions = model.predict(X, verbose=0)
            reconstruction_errors = np.mean(np.square(y - predictions), axis=1)
            threshold = np.percentile(reconstruction_errors, 95)
            self.models["lstm_autoencoder"] = {"model": model, "threshold": threshold}
            return {
                "success": True,
                "message": "LSTM autoencoder trained successfully",
                "final_loss": history.history["loss"][-1],
                "threshold": threshold,
            }
        except Exception as e:
            logger.error(f"Error training LSTM autoencoder: {str(e)}")
            return {"success": False, "error": str(e)}

    def _train_one_class_svm(self, features: np.ndarray) -> Dict[str, Any]:
        """Train One-Class SVM model"""
        try:
            model = OneClassSVM(
                kernel="rbf", gamma="scale", nu=self.config["isolation_contamination"]
            )
            model.fit(features)
            self.models["one_class_svm"] = model
            return {"success": True, "message": "One-Class SVM trained successfully"}
        except Exception as e:
            logger.error(f"Error training One-Class SVM: {str(e)}")
            return {"success": False, "error": str(e)}

    def _detect_isolation_forest(self, features: np.ndarray) -> np.ndarray:
        """Detect anomalies using Isolation Forest"""
        model = self.models["isolation_forest"]
        anomaly_scores = model.decision_function(features)
        model.predict(features)
        scores = (anomaly_scores.max() - anomaly_scores) / (
            anomaly_scores.max() - anomaly_scores.min()
        )
        return scores

    def _detect_autoencoder(self, features: np.ndarray) -> np.ndarray:
        """Detect anomalies using autoencoder"""
        model_info = self.models["autoencoder"]
        model = model_info["model"]
        threshold = model_info["threshold"]
        reconstructions = model.predict(features, verbose=0)
        reconstruction_errors = np.mean(np.square(features - reconstructions), axis=1)
        scores = reconstruction_errors / threshold
        return np.clip(scores, 0, 2)

    def _detect_lstm_autoencoder(
        self, data: pd.DataFrame, target_column: str
    ) -> np.ndarray:
        """Detect anomalies using LSTM autoencoder"""
        model_info = self.models["lstm_autoencoder"]
        model = model_info["model"]
        threshold = model_info["threshold"]
        sequences = self._create_sequences(
            data[target_column].values, self.config["lstm_sequence_length"]
        )
        if len(sequences) == 0:
            return np.zeros(len(data))
        sequences_scaled = (
            self.scalers["lstm"]
            .transform(sequences.reshape(-1, 1))
            .reshape(sequences.shape)
        )
        X = sequences_scaled.reshape(
            sequences_scaled.shape[0], sequences_scaled.shape[1], 1
        )
        predictions = model.predict(X, verbose=0)
        reconstruction_errors = np.mean(
            np.square(sequences_scaled - predictions), axis=1
        )
        scores = np.zeros(len(data))
        start_idx = self.config["lstm_sequence_length"]
        scores[start_idx : start_idx + len(reconstruction_errors)] = (
            reconstruction_errors / threshold
        )
        return scores

    def _detect_one_class_svm(self, features: np.ndarray) -> np.ndarray:
        """Detect anomalies using One-Class SVM"""
        model = self.models["one_class_svm"]
        decision_scores = model.decision_function(features)
        scores = (decision_scores.max() - decision_scores) / (
            decision_scores.max() - decision_scores.min()
        )
        return scores

    def _detect_statistical(self, data: pd.DataFrame, target_column: str) -> np.ndarray:
        """Detect anomalies using statistical methods"""
        values = data[target_column].values
        scores = np.zeros(len(values))
        rolling_mean = pd.Series(values).rolling(self.config["rolling_window"]).mean()
        rolling_std = pd.Series(values).rolling(self.config["rolling_window"]).std()
        z_scores = np.abs((values - rolling_mean) / rolling_std)
        z_scores_normalized = np.clip(
            z_scores / self.config["statistical_threshold"], 0, 1
        )
        if len(values) > self.config["seasonal_period"] * 2:
            try:
                decomposition = seasonal_decompose(
                    pd.Series(values),
                    model="additive",
                    period=min(self.config["seasonal_period"], len(values) // 2),
                )
                residuals = np.abs(decomposition.resid.fillna(0))
                residual_threshold = np.percentile(residuals, 95)
                residual_scores = np.clip(residuals / residual_threshold, 0, 1)
                scores = np.maximum(z_scores_normalized, residual_scores)
            except Exception:
                scores = z_scores_normalized
        else:
            scores = z_scores_normalized
        return scores

    def _combine_results(
        self,
        method_results: Dict[str, np.ndarray],
        data: pd.DataFrame,
        target_column: str,
    ) -> List[AnomalyResult]:
        """Combine results from multiple methods"""
        n_points = len(data)
        combined_scores = np.zeros(n_points)
        if self.config["ensemble_method"] == "voting":
            votes = np.zeros(n_points)
            for _method, scores in method_results.items():
                if len(scores) == n_points:
                    threshold = np.percentile(scores, 90)
                    votes += (scores > threshold).astype(int)
            combined_scores = votes / len(method_results)
        elif self.config["ensemble_method"] == "weighted_average":
            weights = {
                "isolation_forest": 0.3,
                "autoencoder": 0.3,
                "statistical": 0.2,
                "lstm_autoencoder": 0.15,
                "one_class_svm": 0.05,
            }
            for method, scores in method_results.items():
                if len(scores) == n_points:
                    weight = weights.get(method, 1.0 / len(method_results))
                    combined_scores += weight * scores
        else:
            valid_results = [
                scores for scores in method_results.values() if len(scores) == n_points
            ]
            if valid_results:
                combined_scores = np.mean(valid_results, axis=0)
        anomalies = []
        threshold = np.percentile(combined_scores, 95)
        for i, (timestamp, row) in enumerate(data.iterrows()):
            score = combined_scores[i]
            is_anomaly = score > threshold
            severity = self._get_severity(score)
            anomaly_type = self._classify_anomaly_type(i, data, target_column, score)
            explanation = self._generate_explanation(
                i, data, target_column, method_results, score
            )
            anomaly = AnomalyResult(
                timestamp=timestamp,
                value=row[target_column],
                anomaly_score=float(score),
                is_anomaly=is_anomaly,
                anomaly_type=anomaly_type,
                severity=severity,
                confidence=min(score * 1.2, 1.0),
                explanation=explanation,
                context=self._get_context(i, data, target_column),
            )
            anomalies.append(anomaly)
        return anomalies

    def _get_severity(self, score: float) -> AnomalySeverity:
        """Determine anomaly severity based on score"""
        thresholds = self.config["severity_thresholds"]
        if score >= thresholds["critical"]:
            return AnomalySeverity.CRITICAL
        elif score >= thresholds["high"]:
            return AnomalySeverity.HIGH
        elif score >= thresholds["medium"]:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def _classify_anomaly_type(
        self, index: int, data: pd.DataFrame, target_column: str, score: float
    ) -> AnomalyType:
        """Classify the type of anomaly"""
        if index < 5 or index >= len(data) - 5:
            return AnomalyType.POINT_ANOMALY
        window = 5
        max(0, index - window)
        min(len(data), index + window + 1)
        return AnomalyType.POINT_ANOMALY

    def _generate_explanation(
        self,
        index: int,
        data: pd.DataFrame,
        target_column: str,
        method_results: Dict[str, np.ndarray],
        score: float,
    ) -> str:
        """Generate human-readable explanation for the anomaly"""
        explanations = []
        contributing_methods = []
        for method, scores in method_results.items():
            if len(scores) > index:
                method_threshold = np.percentile(scores, 90)
                if scores[index] > method_threshold:
                    contributing_methods.append(method)
        if contributing_methods:
            explanations.append(f"Detected by: {', '.join(contributing_methods)}")
        current_value = data.iloc[index][target_column]
        if index > 20:
            recent_mean = data.iloc[index - 20 : index][target_column].mean()
            deviation = abs(current_value - recent_mean) / recent_mean * 100
            if deviation > 10:
                explanations.append(
                    f"Value deviates {deviation:.1f}% from recent average"
                )
        return "; ".join(explanations) if explanations else "Anomalous pattern detected"

    def _get_context(
        self, index: int, data: pd.DataFrame, target_column: str
    ) -> Dict[str, Any]:
        """Get contextual information for the anomaly"""
        context = {}
        if index > 10:
            recent_data = data.iloc[index - 10 : index + 1]
            context["recent_mean"] = float(recent_data[target_column].mean())
            context["recent_std"] = float(recent_data[target_column].std())
            context["recent_min"] = float(recent_data[target_column].min())
            context["recent_max"] = float(recent_data[target_column].max())
        if "volume" in data.columns:
            context["volume"] = float(data.iloc[index]["volume"])
            if index > 10:
                context["avg_volume"] = float(
                    data.iloc[index - 10 : index + 1]["volume"].mean()
                )
        context["timestamp"] = data.index[index].isoformat()
        if hasattr(data.index[index], "dayofweek"):
            context["day_of_week"] = int(data.index[index].dayofweek)
            context["hour"] = (
                int(data.index[index].hour)
                if hasattr(data.index[index], "hour")
                else None
            )
        return context

    def _create_sequences(self, data: np.ndarray, sequence_length: int) -> np.ndarray:
        """Create sequences for LSTM processing"""
        if len(data) < sequence_length:
            return np.array([])
        sequences = []
        for i in range(sequence_length, len(data)):
            sequences.append(data[i - sequence_length : i])
        return np.array(sequences)

    def save_models(self, filepath: str) -> bool:
        """Save trained models"""
        try:
            import os

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            sklearn_models = {}
            for name, model in self.models.items():
                if name in ["isolation_forest", "one_class_svm"]:
                    sklearn_models[name] = model
            if sklearn_models:
                joblib.dump(sklearn_models, f"{filepath}_sklearn.pkl")
            if "autoencoder" in self.models:
                self.models["autoencoder"]["model"].save(f"{filepath}_autoencoder.h5")
                joblib.dump(
                    {"threshold": self.models["autoencoder"]["threshold"]},
                    f"{filepath}_autoencoder_config.pkl",
                )
            if "lstm_autoencoder" in self.models:
                self.models["lstm_autoencoder"]["model"].save(
                    f"{filepath}_lstm_autoencoder.h5"
                )
                joblib.dump(
                    {"threshold": self.models["lstm_autoencoder"]["threshold"]},
                    f"{filepath}_lstm_config.pkl",
                )
            joblib.dump(self.scalers, f"{filepath}_scalers.pkl")
            joblib.dump(self.config, f"{filepath}_config.pkl")
            logger.info(f"Anomaly detection models saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False

    def load_models(self, filepath: str) -> bool:
        """Load trained models"""
        try:
            self.config = joblib.load(f"{filepath}_config.pkl")
            self.scalers = joblib.load(f"{filepath}_scalers.pkl")
            try:
                sklearn_models = joblib.load(f"{filepath}_sklearn.pkl")
                self.models.update(sklearn_models)
            except FileNotFoundError:
                pass
            try:
                autoencoder = tf.keras.models.load_model(f"{filepath}_autoencoder.h5")
                autoencoder_config = joblib.load(f"{filepath}_autoencoder_config.pkl")
                self.models["autoencoder"] = {
                    "model": autoencoder,
                    "threshold": autoencoder_config["threshold"],
                }
            except FileNotFoundError:
                pass
            try:
                lstm_autoencoder = tf.keras.models.load_model(
                    f"{filepath}_lstm_autoencoder.h5"
                )
                lstm_config = joblib.load(f"{filepath}_lstm_config.pkl")
                self.models["lstm_autoencoder"] = {
                    "model": lstm_autoencoder,
                    "threshold": lstm_config["threshold"],
                }
            except FileNotFoundError:
                pass
            self.is_trained = True
            logger.info(f"Anomaly detection models loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False

    def get_model_performance(
        self,
        data: pd.DataFrame,
        target_column: str,
        true_anomalies: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Evaluate model performance if ground truth is available"""
        try:
            if true_anomalies is None:
                return {"message": "No ground truth provided for evaluation"}
            results = self.detect_anomalies(data, target_column)
            predicted_anomalies = [i for i, r in enumerate(results) if r.is_anomaly]
            true_positives = len(set(true_anomalies) & set(predicted_anomalies))
            false_positives = len(set(predicted_anomalies) - set(true_anomalies))
            false_negatives = len(set(true_anomalies) - set(predicted_anomalies))
            true_negatives = (
                len(data) - true_positives - false_positives - false_negatives
            )
            precision = (
                true_positives / (true_positives + false_positives)
                if true_positives + false_positives > 0
                else 0
            )
            recall = (
                true_positives / (true_positives + false_negatives)
                if true_positives + false_negatives > 0
                else 0
            )
            f1_score = (
                2 * (precision * recall) / (precision + recall)
                if precision + recall > 0
                else 0
            )
            return {
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "true_positives": true_positives,
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "true_negatives": true_negatives,
            }
        except Exception as e:
            logger.error(f"Error evaluating model performance: {str(e)}")
            return {"error": str(e)}
