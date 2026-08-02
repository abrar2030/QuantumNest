import json
import logging
import os
import warnings
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import (
    LSTM,
    BatchNormalization,
    Dense,
    Dropout,
    GlobalAveragePooling1D,
    Input,
    LayerNormalization,
    MultiHeadAttention,
)
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l1_l2

warnings.filterwarnings("ignore")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AdvancedLSTMModel:
    """Advanced LSTM model with attention mechanism and multi-feature support"""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """Initialize advanced LSTM model"""
        self.config = {
            "sequence_length": 60,
            "prediction_horizon": 5,
            "features": [
                "close",
                "volume",
                "open",
                "high",
                "low",
                "returns",
                "volatility",
            ],
            "target": "close",
            "scaling_method": "minmax",
            "model_type": "attention_lstm",
            "lstm_units": [128, 64, 32],
            "attention_heads": 8,
            "dropout_rate": 0.3,
            "recurrent_dropout": 0.2,
            "dense_units": [64, 32],
            "use_batch_norm": True,
            "use_residual": True,
            "epochs": 100,
            "batch_size": 64,
            "validation_split": 0.2,
            "optimizer": "adam",
            "learning_rate": 0.001,
            "loss": "huber",
            "metrics": ["mae", "mse"],
            "l1_reg": 0.01,
            "l2_reg": 0.01,
            "early_stopping_patience": 15,
            "reduce_lr_patience": 10,
            "use_technical_indicators": True,
            "use_fourier_features": True,
            "use_lag_features": True,
            "lag_periods": [1, 2, 3, 5, 10, 20],
            "use_ensemble": True,
            "n_models": 5,
            "ensemble_method": "weighted_average",
        }
        if config:
            self.config.update(config)
        self.models = []
        self.scalers = {}
        self.feature_importance = {}
        self.training_history = []
        self.is_trained = False
        np.random.seed(42)
        tf.random.set_seed(42)

    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Engineer additional features for better prediction"""
        df = data.copy()
        if self.config["use_technical_indicators"]:
            df = self._add_technical_indicators(df)
        if self.config["use_lag_features"]:
            df = self._add_lag_features(df)
        if self.config["use_fourier_features"]:
            df = self._add_fourier_features(df)
        df = self._add_rolling_statistics(df)
        df = self._add_time_features(df)
        return df.dropna()

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators"""
        for window in [5, 10, 20, 50]:
            df[f"sma_{window}"] = df["close"].rolling(window=window).mean()
            df[f"sma_ratio_{window}"] = df["close"] / df[f"sma_{window}"]
        for span in [12, 26]:
            df[f"ema_{span}"] = df["close"].ewm(span=span).mean()
        df["macd"] = df["ema_12"] - df["ema_26"]
        df["macd_signal"] = df["macd"].ewm(span=9).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - 100 / (1 + rs)
        df["bb_middle"] = df["close"].rolling(window=20).mean()
        bb_std = df["close"].rolling(window=20).std()
        df["bb_upper"] = df["bb_middle"] + bb_std * 2
        df["bb_lower"] = df["bb_middle"] - bb_std * 2
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (
            df["bb_upper"] - df["bb_lower"]
        )
        df["volatility"] = df["close"].rolling(window=20).std()
        df["volatility_ratio"] = (
            df["volatility"] / df["volatility"].rolling(window=50).mean()
        )
        df["volume_sma"] = df["volume"].rolling(window=20).mean()
        df["volume_ratio"] = df["volume"] / df["volume_sma"]
        for period in [1, 5, 10, 20]:
            df[f"momentum_{period}"] = df["close"].pct_change(periods=period)
        return df

    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lagged features"""
        for lag in self.config["lag_periods"]:
            df[f"close_lag_{lag}"] = df["close"].shift(lag)
            df[f"volume_lag_{lag}"] = df["volume"].shift(lag)
            df[f"returns_lag_{lag}"] = df["close"].pct_change().shift(lag)
        return df

    def _add_fourier_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Fourier features for seasonality"""
        n = len(df)
        for k in range(1, 4):
            df[f"fourier_sin_{k}"] = np.sin(2 * np.pi * k * np.arange(n) / 252)
            df[f"fourier_cos_{k}"] = np.cos(2 * np.pi * k * np.arange(n) / 252)
        return df

    def _add_rolling_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rolling statistical features"""
        windows = [5, 10, 20]
        for window in windows:
            df[f"close_mean_{window}"] = df["close"].rolling(window=window).mean()
            df[f"close_std_{window}"] = df["close"].rolling(window=window).std()
            df[f"close_min_{window}"] = df["close"].rolling(window=window).min()
            df[f"close_max_{window}"] = df["close"].rolling(window=window).max()
            df[f"close_skew_{window}"] = df["close"].rolling(window=window).skew()
            df[f"close_kurt_{window}"] = df["close"].rolling(window=window).kurt()
            df[f"volume_mean_{window}"] = df["volume"].rolling(window=window).mean()
            df[f"volume_std_{window}"] = df["volume"].rolling(window=window).std()
        return df

    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        if df.index.dtype == "datetime64[ns]":
            df["day_of_week"] = df.index.dayofweek
            df["day_of_month"] = df.index.day
            df["month"] = df.index.month
            df["quarter"] = df.index.quarter
            df["is_month_end"] = df.index.is_month_end.astype(int)
            df["is_quarter_end"] = df.index.is_quarter_end.astype(int)
        return df

    def _prepare_data(
        self, data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare data for training"""
        df = self._engineer_features(data)
        feature_columns = [col for col in df.columns if col != self.config["target"]]
        features = df[feature_columns].values
        target = df[self.config["target"]].values
        if "feature_scaler" not in self.scalers:
            if self.config["scaling_method"] == "minmax":
                self.scalers["feature_scaler"] = MinMaxScaler()
            elif self.config["scaling_method"] == "standard":
                self.scalers["feature_scaler"] = StandardScaler()
            else:
                self.scalers["feature_scaler"] = RobustScaler()
            features_scaled = self.scalers["feature_scaler"].fit_transform(features)
        else:
            features_scaled = self.scalers["feature_scaler"].transform(features)
        if "target_scaler" not in self.scalers:
            self.scalers["target_scaler"] = MinMaxScaler()
            target_scaled = (
                self.scalers["target_scaler"]
                .fit_transform(target.reshape(-1, 1))
                .flatten()
            )
        else:
            target_scaled = (
                self.scalers["target_scaler"].transform(target.reshape(-1, 1)).flatten()
            )
        X, y = self._create_sequences(features_scaled, target_scaled)
        return (X, y, feature_columns)

    def _create_sequences(
        self, features: np.ndarray, target: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM"""
        X, y = ([], [])
        seq_len = self.config["sequence_length"]
        pred_horizon = self.config["prediction_horizon"]
        for i in range(seq_len, len(features) - pred_horizon + 1):
            X.append(features[i - seq_len : i])
            y.append(target[i : i + pred_horizon])
        return (np.array(X), np.array(y))

    def _build_model(self, input_shape: Tuple[int, int]) -> Model:
        """Build the neural network model"""
        if self.config["model_type"] == "attention_lstm":
            return self._build_attention_lstm(input_shape)
        elif self.config["model_type"] == "transformer":
            return self._build_transformer(input_shape)
        elif self.config["model_type"] == "bidirectional_lstm":
            return self._build_bidirectional_lstm(input_shape)
        else:
            return self._build_simple_lstm(input_shape)

    def _build_attention_lstm(self, input_shape: Tuple[int, int]) -> Model:
        """Build LSTM model with attention mechanism"""
        inputs = Input(shape=input_shape)
        x = inputs
        lstm_outputs = []
        for i, units in enumerate(self.config["lstm_units"]):
            lstm_out = LSTM(
                units,
                return_sequences=True,
                dropout=self.config["dropout_rate"],
                recurrent_dropout=self.config["recurrent_dropout"],
                kernel_regularizer=l1_l2(self.config["l1_reg"], self.config["l2_reg"]),
            )(x)
            if self.config["use_batch_norm"]:
                lstm_out = BatchNormalization()(lstm_out)
            lstm_outputs.append(lstm_out)
            if (
                self.config["use_residual"]
                and i > 0
                and (lstm_out.shape[-1] == x.shape[-1])
            ):
                x = tf.keras.layers.Add()([x, lstm_out])
            else:
                x = lstm_out
        attention_out = MultiHeadAttention(
            num_heads=self.config["attention_heads"],
            key_dim=x.shape[-1] // self.config["attention_heads"],
        )(x, x)
        attention_out = LayerNormalization()(attention_out)
        x = tf.keras.layers.Add()([x, attention_out])
        x = GlobalAveragePooling1D()(x)
        for units in self.config["dense_units"]:
            x = Dense(
                units,
                activation="relu",
                kernel_regularizer=l1_l2(self.config["l1_reg"], self.config["l2_reg"]),
            )(x)
            x = Dropout(self.config["dropout_rate"])(x)
            if self.config["use_batch_norm"]:
                x = BatchNormalization()(x)
        outputs = Dense(self.config["prediction_horizon"], activation="linear")(x)
        model = Model(inputs=inputs, outputs=outputs)
        return model

    def _build_transformer(self, input_shape: Tuple[int, int]) -> Model:
        """Build transformer model"""
        inputs = Input(shape=input_shape)
        x = inputs
        for _ in range(3):
            attention_out = MultiHeadAttention(
                num_heads=self.config["attention_heads"],
                key_dim=input_shape[-1] // self.config["attention_heads"],
            )(x, x)
            x = LayerNormalization()(x + attention_out)
            ff = Dense(input_shape[-1] * 2, activation="relu")(x)
            ff = Dense(input_shape[-1])(ff)
            x = LayerNormalization()(x + ff)
        x = GlobalAveragePooling1D()(x)
        for units in self.config["dense_units"]:
            x = Dense(units, activation="relu")(x)
            x = Dropout(self.config["dropout_rate"])(x)
        outputs = Dense(self.config["prediction_horizon"], activation="linear")(x)
        model = Model(inputs=inputs, outputs=outputs)
        return model

    def _build_bidirectional_lstm(self, input_shape: Tuple[int, int]) -> Model:
        """Build bidirectional LSTM model"""
        model = Sequential()
        for i, units in enumerate(self.config["lstm_units"]):
            return_sequences = i < len(self.config["lstm_units"]) - 1
            model.add(
                tf.keras.layers.Bidirectional(
                    LSTM(
                        units,
                        return_sequences=return_sequences,
                        dropout=self.config["dropout_rate"],
                        recurrent_dropout=self.config["recurrent_dropout"],
                    ),
                    input_shape=input_shape if i == 0 else None,
                )
            )
            if self.config["use_batch_norm"]:
                model.add(BatchNormalization())
        for units in self.config["dense_units"]:
            model.add(Dense(units, activation="relu"))
            model.add(Dropout(self.config["dropout_rate"]))
        model.add(Dense(self.config["prediction_horizon"], activation="linear"))
        return model

    def _build_simple_lstm(self, input_shape: Tuple[int, int]) -> Model:
        """Build simple LSTM model"""
        model = Sequential()
        for i, units in enumerate(self.config["lstm_units"]):
            return_sequences = i < len(self.config["lstm_units"]) - 1
            model.add(
                LSTM(
                    units,
                    return_sequences=return_sequences,
                    dropout=self.config["dropout_rate"],
                    input_shape=input_shape if i == 0 else None,
                )
            )
        for units in self.config["dense_units"]:
            model.add(Dense(units, activation="relu"))
            model.add(Dropout(self.config["dropout_rate"]))
        model.add(Dense(self.config["prediction_horizon"], activation="linear"))
        return model

    def train(
        self, data: pd.DataFrame, validation_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Train the model"""
        try:
            logger.info("Starting LSTM model training")
            X, y, feature_columns = self._prepare_data(data)
            if len(X) == 0:
                raise ValueError("No training data available after preprocessing")
            if validation_data is None:
                split_idx = int(len(X) * (1 - self.config["validation_split"]))
                X_train, X_val = (X[:split_idx], X[split_idx:])
                y_train, y_val = (y[:split_idx], y[split_idx:])
            else:
                X_train, y_train = (X, y)
                X_val, y_val, _ = self._prepare_data(validation_data)
            if self.config["use_ensemble"]:
                self.models = []
                histories = []
                for i in range(self.config["n_models"]):
                    logger.info(f"Training model {i + 1}/{self.config['n_models']}")
                    np.random.seed(42 + i)
                    tf.random.set_seed(42 + i)
                    model = self._build_model((X_train.shape[1], X_train.shape[2]))
                    optimizer = Adam(learning_rate=self.config["learning_rate"])
                    model.compile(
                        optimizer=optimizer,
                        loss=self.config["loss"],
                        metrics=self.config["metrics"],
                    )
                    callbacks = [
                        EarlyStopping(
                            monitor="val_loss",
                            patience=self.config["early_stopping_patience"],
                            restore_best_weights=True,
                        ),
                        ReduceLROnPlateau(
                            monitor="val_loss",
                            factor=0.5,
                            patience=self.config["reduce_lr_patience"],
                            min_lr=1e-07,
                        ),
                    ]
                    history = model.fit(
                        X_train,
                        y_train,
                        validation_data=(X_val, y_val),
                        epochs=self.config["epochs"],
                        batch_size=self.config["batch_size"],
                        callbacks=callbacks,
                        verbose=0,
                    )
                    self.models.append(model)
                    histories.append(history.history)
                self.training_history = histories
            else:
                model = self._build_model((X_train.shape[1], X_train.shape[2]))
                optimizer = Adam(learning_rate=self.config["learning_rate"])
                model.compile(
                    optimizer=optimizer,
                    loss=self.config["loss"],
                    metrics=self.config["metrics"],
                )
                callbacks = [
                    EarlyStopping(
                        monitor="val_loss",
                        patience=self.config["early_stopping_patience"],
                        restore_best_weights=True,
                    ),
                    ReduceLROnPlateau(
                        monitor="val_loss",
                        factor=0.5,
                        patience=self.config["reduce_lr_patience"],
                        min_lr=1e-07,
                    ),
                ]
                history = model.fit(
                    X_train,
                    y_train,
                    validation_data=(X_val, y_val),
                    epochs=self.config["epochs"],
                    batch_size=self.config["batch_size"],
                    callbacks=callbacks,
                    verbose=1,
                )
                self.models = [model]
                self.training_history = [history.history]
            self.is_trained = True
            train_metrics = self.evaluate(X_train, y_train)
            val_metrics = self.evaluate(X_val, y_val)
            logger.info("LSTM model training completed successfully")
            return {
                "success": True,
                "train_metrics": train_metrics,
                "validation_metrics": val_metrics,
                "training_history": self.training_history,
                "feature_columns": feature_columns,
            }
        except Exception as e:
            logger.error(f"Error training LSTM model: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Make predictions"""
        try:
            if not self.is_trained or not self.models:
                raise ValueError("Model must be trained before making predictions")
            X, _, _ = self._prepare_data(data)
            if len(X) == 0:
                raise ValueError("No data available for prediction after preprocessing")
            predictions = []
            for model in self.models:
                pred = model.predict(X, verbose=0)
                predictions.append(pred)
            if self.config["ensemble_method"] == "simple_average":
                ensemble_pred = np.mean(predictions, axis=0)
            elif self.config["ensemble_method"] == "weighted_average":
                weights = np.ones(len(predictions)) / len(predictions)
                ensemble_pred = np.average(predictions, axis=0, weights=weights)
            else:
                ensemble_pred = np.mean(predictions, axis=0)
            pred_reshaped = ensemble_pred.reshape(-1, 1)
            predictions_original = self.scalers["target_scaler"].inverse_transform(
                pred_reshaped
            )
            predictions_original = predictions_original.reshape(ensemble_pred.shape)
            return {
                "success": True,
                "predictions": predictions_original.tolist(),
                "prediction_dates": self._generate_prediction_dates(data),
                "confidence_intervals": self._calculate_confidence_intervals(
                    predictions
                ),
            }
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        try:
            if not self.models:
                return {}
            predictions = []
            for model in self.models:
                pred = model.predict(X, verbose=0)
                predictions.append(pred)
            ensemble_pred = np.mean(predictions, axis=0)
            mse = mean_squared_error(y.flatten(), ensemble_pred.flatten())
            mae = mean_absolute_error(y.flatten(), ensemble_pred.flatten())
            rmse = np.sqrt(mse)
            r2_scores = []
            for i in range(y.shape[1]):
                r2 = r2_score(y[:, i], ensemble_pred[:, i])
                r2_scores.append(r2)
            return {
                "mse": float(mse),
                "mae": float(mae),
                "rmse": float(rmse),
                "r2_mean": float(np.mean(r2_scores)),
                "r2_scores": [float(r2) for r2 in r2_scores],
            }
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            return {}

    def _generate_prediction_dates(self, data: pd.DataFrame) -> List[str]:
        """Generate dates for predictions"""
        if hasattr(data.index, "freq") and data.index.freq:
            last_date = data.index[-1]
            dates = pd.date_range(
                start=last_date + data.index.freq,
                periods=self.config["prediction_horizon"],
                freq=data.index.freq,
            )
            return [date.strftime("%Y-%m-%d") for date in dates]
        else:
            last_date = pd.to_datetime(data.index[-1])
            dates = [
                (last_date + timedelta(days=i + 1)).strftime("%Y-%m-%d")
                for i in range(self.config["prediction_horizon"])
            ]
            return dates

    def _calculate_confidence_intervals(
        self, predictions: List[np.ndarray], confidence: float = 0.95
    ) -> Dict[str, List]:
        """Calculate confidence intervals for predictions"""
        try:
            predictions_array = np.array(predictions)
            lower_percentile = (1 - confidence) / 2 * 100
            upper_percentile = (1 + confidence) / 2 * 100
            lower_bounds = np.percentile(predictions_array, lower_percentile, axis=0)
            upper_bounds = np.percentile(predictions_array, upper_percentile, axis=0)
            lower_original = (
                self.scalers["target_scaler"]
                .inverse_transform(lower_bounds.reshape(-1, 1))
                .reshape(lower_bounds.shape)
            )
            upper_original = (
                self.scalers["target_scaler"]
                .inverse_transform(upper_bounds.reshape(-1, 1))
                .reshape(upper_bounds.shape)
            )
            return {
                "lower_bounds": lower_original.tolist(),
                "upper_bounds": upper_original.tolist(),
                "confidence_level": confidence,
            }
        except Exception as e:
            logger.error(f"Error calculating confidence intervals: {str(e)}")
            return {
                "lower_bounds": [],
                "upper_bounds": [],
                "confidence_level": confidence,
            }

    def save_model(self, filepath: str) -> bool:
        """Save the trained model"""
        try:
            if not self.models:
                logger.warning("No trained models to save")
                return False
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            for i, model in enumerate(self.models):
                model_path = f"{filepath}_model_{i}.h5"
                model.save(model_path)
            joblib.dump(self.scalers, f"{filepath}_scalers.pkl")
            with open(f"{filepath}_config.json", "w") as f:
                json.dump(self.config, f, indent=2)
            with open(f"{filepath}_history.json", "w") as f:
                json.dump(self.training_history, f, indent=2)
            logger.info(f"Model saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False

    def load_model(self, filepath: str) -> bool:
        """Load a trained model"""
        try:
            with open(f"{filepath}_config.json", "r") as f:
                self.config = json.load(f)
            self.scalers = joblib.load(f"{filepath}_scalers.pkl")
            self.models = []
            i = 0
            while os.path.exists(f"{filepath}_model_{i}.h5"):
                model = tf.keras.models.load_model(f"{filepath}_model_{i}.h5")
                self.models.append(model)
                i += 1
            if os.path.exists(f"{filepath}_history.json"):
                with open(f"{filepath}_history.json", "r") as f:
                    self.training_history = json.load(f)
            self.is_trained = True
            logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance (approximation for neural networks)"""
        return self.feature_importance

    def hyperparameter_tuning(
        self, data: pd.DataFrame, param_grid: Dict[str, List]
    ) -> Dict[str, Any]:
        """Perform hyperparameter tuning"""
        try:
            logger.info("Starting hyperparameter tuning")
            best_score = float("inf")
            best_params = {}
            results = []
            from itertools import product

            param_combinations = list(product(*param_grid.values()))
            for i, params in enumerate(param_combinations):
                logger.info(f"Testing combination {i + 1}/{len(param_combinations)}")
                param_dict = dict(zip(param_grid.keys(), params, strict=False))
                original_config = self.config.copy()
                self.config.update(param_dict)
                result = self.train(data)
                if result["success"]:
                    val_loss = result["validation_metrics"].get("mse", float("inf"))
                    results.append(
                        {
                            "params": param_dict,
                            "validation_loss": val_loss,
                            "metrics": result["validation_metrics"],
                        }
                    )
                    if val_loss < best_score:
                        best_score = val_loss
                        best_params = param_dict.copy()
                self.config = original_config
            self.config.update(best_params)
            logger.info(f"Hyperparameter tuning completed. Best params: {best_params}")
            return {
                "success": True,
                "best_params": best_params,
                "best_score": best_score,
                "all_results": results,
            }
        except Exception as e:
            logger.error(f"Error in hyperparameter tuning: {str(e)}")
            return {"success": False, "error": str(e)}
