import json
import logging
import os
from datetime import timedelta
from typing import Any

import joblib
import numpy as np
import pandas as pd
from app.core.time_utils import utc_now
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AIRecommendationEngine:

    def __init__(self, config: Any = None) -> None:
        """
        Initialize AI recommendation engine

        Parameters:
        -----------
        config : dict
            Configuration parameters for the model
        """
        self.config = {
            "model_type": "ensemble",
            "prediction_horizon": 30,
            "features": [
                "price_momentum",
                "volume_trend",
                "volatility",
                "rsi",
                "macd",
                "sentiment_score",
                "market_correlation",
            ],
            "ensemble_weights": {"random_forest": 0.5, "gradient_boosting": 0.5},
            "random_state": 42,
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
        }
        if config:
            self.config.update(config)
        self.models = {}
        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()
        self.feature_importance = None

    def _preprocess_data(self, data: Any) -> Any:
        """
        Preprocess data for model training

        Parameters:
        -----------
        data : pandas.DataFrame
            Input data with features and target

        Returns:
        --------
        X : numpy.ndarray
            Preprocessed features
        y : numpy.ndarray
            Preprocessed target
        """
        X = data[self.config["features"]].values
        y = data["target"].values.reshape(-1, 1)
        X_scaled = self.feature_scaler.fit_transform(X)
        y_scaled = self.target_scaler.fit_transform(y)
        return (X_scaled, y_scaled.ravel())

    def _create_models(self) -> Any:
        """
        Create machine learning models

        Returns:
        --------
        models : dict
            Dictionary of models
        """
        models = {}
        if self.config["model_type"] in ["random_forest", "ensemble"]:
            models["random_forest"] = RandomForestRegressor(
                n_estimators=self.config["n_estimators"],
                max_depth=self.config["max_depth"],
                min_samples_split=self.config["min_samples_split"],
                min_samples_leaf=self.config["min_samples_leaf"],
                random_state=self.config["random_state"],
            )
        if self.config["model_type"] in ["gradient_boosting", "ensemble"]:
            models["gradient_boosting"] = GradientBoostingRegressor(
                n_estimators=self.config["n_estimators"],
                max_depth=self.config["max_depth"],
                min_samples_split=self.config["min_samples_split"],
                min_samples_leaf=self.config["min_samples_leaf"],
                random_state=self.config["random_state"],
            )
        return models

    def train(self, data: Any) -> Any:
        """
        Train recommendation models

        Parameters:
        -----------
        data : pandas.DataFrame
            Training data with features and target

        Returns:
        --------
        self : AIRecommendationEngine
            Trained model
        """
        X, y = self._preprocess_data(data)
        self.models = self._create_models()
        for _name, model in self.models.items():
            model.fit(X, y)
        self._calculate_feature_importance()
        return self

    def _calculate_feature_importance(self) -> Any:
        """
        Calculate feature importance

        Returns:
        --------
        feature_importance : dict
            Feature importance for each model
        """
        feature_importance = {}
        for name, model in self.models.items():
            if hasattr(model, "feature_importances_"):
                importance = model.feature_importances_
                feature_importance[name] = {
                    feature: float(imp)
                    for feature, imp in zip(
                        self.config["features"], importance, strict=False
                    )
                }
        self.feature_importance = feature_importance
        return feature_importance

    def predict(self, features: Any) -> Any:
        """
        Generate recommendations based on features

        Parameters:
        -----------
        features : pandas.DataFrame
            Input features

        Returns:
        --------
        recommendations : dict
            Recommendation results
        """
        if not self.models:
            raise ValueError("Models not trained yet. Call train() first.")
        X = features[self.config["features"]].values
        X_scaled = self.feature_scaler.transform(X)
        predictions = {}
        for name, model in self.models.items():
            pred = model.predict(X_scaled)
            predictions[name] = pred
        if self.config["model_type"] == "ensemble":
            ensemble_pred = np.zeros_like(predictions[list(predictions.keys())[0]])
            for name, pred in predictions.items():
                weight = self.config["ensemble_weights"].get(
                    name, 1.0 / len(predictions)
                )
                ensemble_pred += pred * weight
            predictions["ensemble"] = ensemble_pred
        for name, pred in predictions.items():
            predictions[name] = self.target_scaler.inverse_transform(
                pred.reshape(-1, 1)
            ).ravel()
        if self.config["model_type"] == "ensemble":
            final_predictions = predictions["ensemble"]
        else:
            final_predictions = predictions[self.config["model_type"]]
        recommendations = self._format_recommendations(features, final_predictions)
        return recommendations

    def _format_recommendations(self, features: Any, predictions: Any) -> Any:
        """
        Format recommendations

        Parameters:
        -----------
        features : pandas.DataFrame
            Input features
        predictions : numpy.ndarray
            Model predictions

        Returns:
        --------
        recommendations : dict
            Formatted recommendations
        """
        if "symbol" in features.columns:
            symbols = features["symbol"].tolist()
        else:
            symbols = [f"Asset_{i + 1}" for i in range(len(predictions))]
        items = []
        for i, (symbol, prediction) in enumerate(
            zip(symbols, predictions, strict=False)
        ):
            if prediction > 0.05:
                rec_type = "buy"
            elif prediction < -0.05:
                rec_type = "sell"
            else:
                rec_type = "hold"
            confidence = min(abs(prediction) * 10, 1.0) * 100
            item = {
                "symbol": symbol,
                "recommendation": rec_type,
                "predicted_return": float(prediction),
                "confidence": float(confidence),
                "time_horizon": f"{self.config['prediction_horizon']} days",
                "timestamp": utc_now().isoformat(),
            }
            if all((f in features.columns for f in self.config["features"])):
                item["features"] = {
                    feature: float(features[feature].iloc[i])
                    for feature in self.config["features"]
                }
            items.append(item)
        items.sort(key=lambda x: abs(x["predicted_return"]), reverse=True)
        recommendations = {
            "timestamp": utc_now().isoformat(),
            "prediction_horizon": self.config["prediction_horizon"],
            "model_type": self.config["model_type"],
            "recommendations": items,
            "market_outlook": self._generate_market_outlook(predictions),
        }
        return recommendations

    def _generate_market_outlook(self, predictions: Any) -> Any:
        """
        Generate market outlook based on predictions

        Parameters:
        -----------
        predictions : numpy.ndarray
            Model predictions

        Returns:
        --------
        market_outlook : dict
            Market outlook information
        """
        avg_prediction = np.mean(predictions)
        if avg_prediction > 0.03:
            outlook = "bullish"
        elif avg_prediction < -0.03:
            outlook = "bearish"
        else:
            outlook = "neutral"
        confidence = min(abs(avg_prediction) * 15, 1.0) * 100
        today = utc_now()
        forecast_dates = [
            (today + timedelta(days=7)).strftime("%Y-%m-%d"),
            (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            (today + timedelta(days=30)).strftime("%Y-%m-%d"),
        ]
        market_outlook = {
            "overall_outlook": outlook,
            "confidence": float(confidence),
            "average_predicted_return": float(avg_prediction),
            "volatility_expectation": (
                "high" if np.std(predictions) > 0.05 else "moderate"
            ),
            "forecast_period": {
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": (
                    today + timedelta(days=self.config["prediction_horizon"])
                ).strftime("%Y-%m-%d"),
            },
            "key_indicators": {
                "positive_recommendations": int(np.sum(predictions > 0.05)),
                "negative_recommendations": int(np.sum(predictions < -0.05)),
                "neutral_recommendations": int(
                    np.sum((predictions >= -0.05) & (predictions <= 0.05))
                ),
            },
            "forecast_trend": [
                {
                    "date": forecast_dates[0],
                    "outlook": outlook,
                    "confidence": float(confidence * 0.9),
                },
                {
                    "date": forecast_dates[1],
                    "outlook": outlook,
                    "confidence": float(confidence * 0.8),
                },
                {
                    "date": forecast_dates[2],
                    "outlook": outlook,
                    "confidence": float(confidence * 0.7),
                },
            ],
        }
        return market_outlook

    def get_feature_importance(self) -> Any:
        """
        Get feature importance

        Returns:
        --------
        importance : dict
            Feature importance information
        """
        if self.feature_importance is None:
            raise ValueError(
                "Feature importance not calculated yet. Train models first."
            )
        if len(self.feature_importance) > 1:
            avg_importance = {}
            for feature in self.config["features"]:
                avg_importance[feature] = np.mean(
                    [imp[feature] for imp in self.feature_importance.values()]
                )
            self.feature_importance["ensemble"] = avg_importance
        if self.config["model_type"] == "ensemble":
            importance = self.feature_importance["ensemble"]
        else:
            importance = self.feature_importance[self.config["model_type"]]
        sorted_importance = {
            k: v
            for k, v in sorted(
                importance.items(), key=lambda item: item[1], reverse=True
            )
        }
        return sorted_importance

    def save(self, path: Any) -> Any:
        """
        Save model

        Parameters:
        -----------
        path : str
            Directory path to save model
        """
        if not self.models:
            raise ValueError("Models not trained yet. Call train() first.")
        os.makedirs(path, exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, os.path.join(path, f"recommendation_{name}_model.pkl"))
        joblib.dump(
            self.feature_scaler, os.path.join(path, "recommendation_feature_scaler.pkl")
        )
        joblib.dump(
            self.target_scaler, os.path.join(path, "recommendation_target_scaler.pkl")
        )
        model_data = {
            "config": self.config,
            "feature_importance": self.feature_importance,
        }
        with open(os.path.join(path, "recommendation_data.json"), "w") as f:
            json.dump(model_data, f)

    @classmethod
    def load(cls: Any, path: Any) -> Any:
        """
        Load model

        Parameters:
        -----------
        path : str
            Directory path to load model from

        Returns:
        --------
        model : AIRecommendationEngine
            Loaded model
        """
        with open(os.path.join(path, "recommendation_data.json"), "r") as f:
            model_data = json.load(f)
        instance = cls(model_data["config"])
        instance.feature_importance = model_data["feature_importance"]
        instance.models = {}
        if instance.config["model_type"] in ["random_forest", "ensemble"]:
            instance.models["random_forest"] = joblib.load(
                os.path.join(path, "recommendation_random_forest_model.pkl")
            )
        if instance.config["model_type"] in ["gradient_boosting", "ensemble"]:
            instance.models["gradient_boosting"] = joblib.load(
                os.path.join(path, "recommendation_gradient_boosting_model.pkl")
            )
        instance.feature_scaler = joblib.load(
            os.path.join(path, "recommendation_feature_scaler.pkl")
        )
        instance.target_scaler = joblib.load(
            os.path.join(path, "recommendation_target_scaler.pkl")
        )
        return instance


if __name__ == "__main__":
    np.random.seed(42)
    n_samples = 1000
    n_assets = 50
    features = []
    targets = []
    for i in range(n_assets):
        price_momentum = np.random.normal(0.01, 0.05, n_samples)
        volume_trend = np.random.normal(0.02, 0.1, n_samples)
        volatility = np.random.uniform(0.1, 0.5, n_samples)
        rsi = np.random.uniform(30, 70, n_samples)
        macd = np.random.normal(0, 0.1, n_samples)
        sentiment_score = np.random.normal(0.5, 0.2, n_samples)
        market_correlation = np.random.uniform(-0.5, 0.9, n_samples)
        target = (
            0.3 * price_momentum
            + 0.1 * volume_trend
            - 0.2 * volatility
            + 0.002 * (rsi - 50)
            + 0.5 * macd
            + 0.2 * sentiment_score
            + 0.1 * market_correlation
            + np.random.normal(0, 0.02, n_samples)
        )
        for j in range(n_samples):
            features.append(
                {
                    "symbol": f"ASSET_{i + 1}",
                    "price_momentum": price_momentum[j],
                    "volume_trend": volume_trend[j],
                    "volatility": volatility[j],
                    "rsi": rsi[j],
                    "macd": macd[j],
                    "sentiment_score": sentiment_score[j],
                    "market_correlation": market_correlation[j],
                    "target": target[j],
                }
            )
    data = pd.DataFrame(features)
    train_data = data.sample(frac=0.8, random_state=42)
    test_data = data.drop(train_data.index)
    engine = AIRecommendationEngine()
    engine.train(train_data)
    importance = engine.get_feature_importance()
    for feature, imp in importance.items():
        logger.info(f"Feature: {feature}, Importance: {imp}")
    test_features = test_data.drop("target", axis=1)
    recommendations = engine.predict(test_features)
    for i, rec in enumerate(recommendations["recommendations"][:5]):
        logger.info(
            f"Recommendation {i + 1}: {rec['symbol']} - {rec['recommendation']} ({rec['confidence']:.2f}%)"
        )
    engine.save("recommendation_engine")
    loaded_engine = AIRecommendationEngine.load("recommendation_engine")
    loaded_recommendations = loaded_engine.predict(test_features)
