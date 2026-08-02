import json
import logging
import os
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RiskProfiler:

    def __init__(self, config: Any = None) -> None:
        """
        Initialize risk profiling system

        Parameters:
        -----------
        config : dict
            Configuration parameters for the model
        """
        self.config = {
            "num_profiles": 5,
            "profile_labels": [
                "Very Conservative",
                "Conservative",
                "Moderate",
                "Aggressive",
                "Very Aggressive",
            ],
            "questionnaire_weights": {
                "age": 0.15,
                "income": 0.1,
                "net_worth": 0.15,
                "investment_horizon": 0.2,
                "risk_tolerance": 0.25,
                "investment_knowledge": 0.15,
            },
            "clustering_method": "kmeans",
            "random_state": 42,
        }
        if config:
            self.config.update(config)
        self.scaler = StandardScaler()
        self.pca = None
        self.clustering_model = None
        self.profile_centers = None
        self.feature_names = None

    def _preprocess_data(self, data: Any) -> Any:
        """
        Preprocess data for clustering

        Parameters:
        -----------
        data : pandas.DataFrame
            Input data with user features

        Returns:
        --------
        scaled_data : numpy.ndarray
            Preprocessed data
        """
        self.feature_names = data.columns.tolist()
        scaled_data = self.scaler.fit_transform(data)
        return scaled_data

    def _create_clustering_model(self) -> Any:
        """
        Create clustering model

        Returns:
        --------
        model : sklearn.cluster.KMeans
            Clustering model
        """
        if self.config["clustering_method"] == "kmeans":
            model = KMeans(
                n_clusters=self.config["num_profiles"],
                random_state=self.config["random_state"],
            )
        else:
            raise ValueError(
                f"Unsupported clustering method: {self.config['clustering_method']}"
            )
        return model

    def fit(self, data: Any) -> Any:
        """
        Fit risk profiling model

        Parameters:
        -----------
        data : pandas.DataFrame
            Input data with user features

        Returns:
        --------
        self : RiskProfiler
            Fitted model
        """
        scaled_data = self._preprocess_data(data)
        self.clustering_model = self._create_clustering_model()
        self.clustering_model.fit(scaled_data)
        self.profile_centers = self.clustering_model.cluster_centers_
        if scaled_data.shape[1] > 2:
            self.pca = PCA(n_components=2)
            self.pca.fit(scaled_data)
        return self

    def predict(self, user_data: Any) -> Any:
        """
        Predict risk profile for user

        Parameters:
        -----------
        user_data : pandas.DataFrame or dict
            User data with features

        Returns:
        --------
        profile : dict
            Risk profile information
        """
        if self.clustering_model is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        if isinstance(user_data, dict):
            user_data = pd.DataFrame([user_data])
        missing_features = set(self.feature_names) - set(user_data.columns)
        if missing_features:
            raise ValueError(f"Missing features in user data: {missing_features}")
        user_data = user_data[self.feature_names]
        scaled_user_data = self.scaler.transform(user_data)
        cluster = self.clustering_model.predict(scaled_user_data)[0]
        profile_label = self.config["profile_labels"][cluster]
        center_distance = np.linalg.norm(
            scaled_user_data - self.profile_centers[cluster]
        )
        max_distance = np.sqrt(len(self.feature_names))
        confidence = max(0, 1 - center_distance / max_distance)
        profile = {
            "profile_id": int(cluster),
            "profile_label": profile_label,
            "confidence": float(confidence),
            "feature_contributions": self._calculate_feature_contributions(
                scaled_user_data[0], cluster
            ),
        }
        return profile

    def _calculate_feature_contributions(self, user_features: Any, cluster: Any) -> Any:
        """
        Calculate feature contributions to profile assignment

        Parameters:
        -----------
        user_features : numpy.ndarray
            Scaled user features
        cluster : int
            Assigned cluster

        Returns:
        --------
        contributions : dict
            Feature contributions
        """
        center = self.profile_centers[cluster]
        differences = np.abs(user_features - center)
        total_difference = np.sum(differences)
        if total_difference > 0:
            contributions = 1 - differences / total_difference
        else:
            contributions = np.ones_like(differences)
        return {
            feature: float(contrib)
            for feature, contrib in zip(self.feature_names, contributions, strict=False)
        }

    def get_profile_recommendations(self, profile_id: Any) -> Any:
        """
        Get investment recommendations for risk profile

        Parameters:
        -----------
        profile_id : int
            Risk profile ID

        Returns:
        --------
        recommendations : dict
            Investment recommendations
        """
        if self.clustering_model is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        if profile_id < 0 or profile_id >= self.config["num_profiles"]:
            raise ValueError(
                f"Invalid profile ID: {profile_id}. Must be between 0 and {self.config['num_profiles'] - 1}."
            )
        asset_allocations = {
            0: {"stocks": 20, "bonds": 60, "cash": 15, "alternatives": 5},
            1: {"stocks": 35, "bonds": 50, "cash": 10, "alternatives": 5},
            2: {"stocks": 50, "bonds": 35, "cash": 5, "alternatives": 10},
            3: {"stocks": 70, "bonds": 20, "cash": 0, "alternatives": 10},
            4: {"stocks": 85, "bonds": 5, "cash": 0, "alternatives": 10},
        }
        investment_strategies = {
            0: [
                "Focus on capital preservation and income generation",
                "Invest in high-quality bonds and dividend-paying stocks",
                "Maintain higher cash reserves for stability",
                "Minimize exposure to market volatility",
            ],
            1: [
                "Balance between capital preservation and modest growth",
                "Diversify across fixed income and blue-chip stocks",
                "Maintain moderate cash reserves",
                "Consider inflation-protected securities",
            ],
            2: [
                "Balance between growth and income",
                "Diversify across domestic and international markets",
                "Consider both value and growth investments",
                "Maintain small cash position for opportunities",
            ],
            3: [
                "Focus on long-term capital appreciation",
                "Overweight growth stocks and emerging markets",
                "Consider alternative investments for diversification",
                "Accept higher volatility for potential higher returns",
            ],
            4: [
                "Maximize long-term growth potential",
                "Invest in high-growth sectors and emerging markets",
                "Consider leveraged positions and concentrated bets",
                "Accept significant volatility for maximum return potential",
            ],
        }
        investment_vehicles = {
            0: [
                "Treasury bonds and notes",
                "Municipal bonds",
                "High-quality corporate bonds",
                "Certificates of deposit",
                "Money market funds",
                "Dividend aristocrat stocks",
            ],
            1: [
                "Investment-grade corporate bonds",
                "Government bonds",
                "Blue-chip dividend stocks",
                "High-yield savings accounts",
                "Balanced mutual funds",
                "REITs for income",
            ],
            2: [
                "Diversified stock index funds",
                "Balanced ETFs",
                "Corporate and government bonds",
                "International developed market funds",
                "Select REITs and preferred stocks",
                "Target-date funds",
            ],
            3: [
                "Growth stock funds",
                "Small and mid-cap stock funds",
                "Emerging market funds",
                "High-yield bonds",
                "Commodities",
                "Select alternative investments",
            ],
            4: [
                "Aggressive growth stocks",
                "Sector-specific funds (technology, biotech)",
                "Emerging market stocks",
                "Private equity",
                "Cryptocurrency allocation",
                "Leveraged ETFs",
            ],
        }
        recommendations = {
            "profile_id": profile_id,
            "profile_label": self.config["profile_labels"][profile_id],
            "asset_allocation": asset_allocations[profile_id],
            "investment_strategies": investment_strategies[profile_id],
            "recommended_vehicles": investment_vehicles[profile_id],
            "risk_metrics": {
                "expected_annual_return": 2 + profile_id * 2,
                "expected_volatility": 2 + profile_id * 3,
                "max_drawdown": 5 + profile_id * 5,
                "investment_horizon": 1 + profile_id * 2,
            },
        }
        return recommendations

    def process_questionnaire(self, responses: Any) -> Any:
        """
        Process risk questionnaire responses

        Parameters:
        -----------
        responses : dict
            Questionnaire responses

        Returns:
        --------
        profile : dict
            Risk profile information
        """
        scoring = {
            "age": {
                "under_30": 5,
                "30_to_40": 4,
                "41_to_50": 3,
                "51_to_60": 2,
                "over_60": 1,
            },
            "income": {
                "under_50k": 1,
                "50k_to_100k": 2,
                "100k_to_200k": 3,
                "200k_to_500k": 4,
                "over_500k": 5,
            },
            "net_worth": {
                "under_100k": 1,
                "100k_to_500k": 2,
                "500k_to_1m": 3,
                "1m_to_5m": 4,
                "over_5m": 5,
            },
            "investment_horizon": {
                "less_than_1_year": 1,
                "1_to_3_years": 2,
                "3_to_5_years": 3,
                "5_to_10_years": 4,
                "more_than_10_years": 5,
            },
            "risk_tolerance": {
                "very_low": 1,
                "low": 2,
                "medium": 3,
                "high": 4,
                "very_high": 5,
            },
            "investment_knowledge": {
                "novice": 1,
                "basic": 2,
                "intermediate": 3,
                "advanced": 4,
                "expert": 5,
            },
        }
        scores = {}
        for category, response in responses.items():
            if category in scoring and response in scoring[category]:
                scores[category] = scoring[category][response]
            else:
                raise ValueError(
                    f"Invalid response '{response}' for category '{category}'"
                )
        weighted_score = 0
        for category, score in scores.items():
            if category in self.config["questionnaire_weights"]:
                weighted_score += score * self.config["questionnaire_weights"][category]
        normalized_score = (weighted_score - 1) / 4
        profile_id = min(
            int(normalized_score * self.config["num_profiles"]),
            self.config["num_profiles"] - 1,
        )
        profile_label = self.config["profile_labels"][profile_id]
        profile = {
            "profile_id": profile_id,
            "profile_label": profile_label,
            "score": weighted_score,
            "normalized_score": normalized_score,
            "category_scores": scores,
            "recommendations": self.get_profile_recommendations(profile_id),
        }
        return profile

    def plot_profiles(self, data: Any = None, figsize: Any = (12, 10)) -> Any:
        """
        Plot risk profiles

        Parameters:
        -----------
        data : pandas.DataFrame
            User data with features and cluster assignments
        figsize : tuple
            Figure size

        Returns:
        --------
        fig : matplotlib.figure.Figure
            Figure object
        """
        if self.clustering_model is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        fig, ax = plt.subplots(figsize=figsize)
        if data is not None:
            scaled_data = self.scaler.transform(data[self.feature_names])
            clusters = self.clustering_model.predict(scaled_data)
            if self.pca is not None:
                points = self.pca.transform(scaled_data)
                centers = self.pca.transform(self.profile_centers)
            else:
                points = scaled_data
                centers = self.profile_centers
            for i in range(self.config["num_profiles"]):
                mask = clusters == i
                ax.scatter(
                    points[mask, 0],
                    points[mask, 1],
                    alpha=0.7,
                    s=50,
                    label=f"Profile {i + 1}: {self.config['profile_labels'][i]}",
                )
            ax.scatter(
                centers[:, 0],
                centers[:, 1],
                s=200,
                c="red",
                marker="X",
                label="Profile Centers",
            )
        else:
            if self.pca is not None:
                centers = self.pca.transform(self.profile_centers)
            else:
                centers = self.profile_centers
            for i in range(self.config["num_profiles"]):
                ax.scatter(
                    centers[i, 0],
                    centers[i, 1],
                    s=200,
                    marker="X",
                    label=f"Profile {i + 1}: {self.config['profile_labels'][i]}",
                )
        if self.pca is not None:
            ax.set_xlabel("Principal Component 1")
            ax.set_ylabel("Principal Component 2")
        else:
            ax.set_xlabel(self.feature_names[0])
            ax.set_ylabel(self.feature_names[1])
        ax.set_title("Risk Profiles")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        return fig

    def plot_asset_allocation(
        self, profile_id: Any = None, figsize: Any = (10, 8)
    ) -> Any:
        """
        Plot asset allocation for risk profile

        Parameters:
        -----------
        profile_id : int or None
            Risk profile ID. If None, plot all profiles.
        figsize : tuple
            Figure size

        Returns:
        --------
        fig : matplotlib.figure.Figure
            Figure object
        """
        asset_allocations = {
            0: {"stocks": 20, "bonds": 60, "cash": 15, "alternatives": 5},
            1: {"stocks": 35, "bonds": 50, "cash": 10, "alternatives": 5},
            2: {"stocks": 50, "bonds": 35, "cash": 5, "alternatives": 10},
            3: {"stocks": 70, "bonds": 20, "cash": 0, "alternatives": 10},
            4: {"stocks": 85, "bonds": 5, "cash": 0, "alternatives": 10},
        }
        fig, ax = plt.subplots(figsize=figsize)
        if profile_id is not None:
            if profile_id < 0 or profile_id >= self.config["num_profiles"]:
                raise ValueError(
                    f"Invalid profile ID: {profile_id}. Must be between 0 and {self.config['num_profiles'] - 1}."
                )
            allocation = asset_allocations[profile_id]
            ax.pie(
                allocation.values(),
                labels=allocation.keys(),
                autopct="%1.1f%%",
                startangle=90,
                colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"],
            )
            ax.set_title(
                f"Asset Allocation for {self.config['profile_labels'][profile_id]} Profile"
            )
        else:
            profiles = list(range(self.config["num_profiles"]))
            assets = list(asset_allocations[0].keys())
            x = np.arange(len(profiles))
            width = 0.2
            multiplier = 0
            for asset in assets:
                asset_values = [asset_allocations[p][asset] for p in profiles]
                offset = width * multiplier
                rects = ax.bar(
                    x + offset, asset_values, width, label=asset.capitalize()
                )
                ax.bar_label(rects, padding=3)
                multiplier += 1
            ax.set_xlabel("Risk Profile")
            ax.set_ylabel("Allocation (%)")
            ax.set_title("Asset Allocation by Risk Profile")
            ax.set_xticks(x + width * (len(assets) - 1) / 2)
            ax.set_xticklabels(self.config["profile_labels"])
            ax.legend(loc="upper left")
            ax.grid(True, axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        return fig

    def save(self, path: Any) -> Any:
        """
        Save model

        Parameters:
        -----------
        path : str
            Directory path to save model
        """
        if self.clustering_model is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        os.makedirs(path, exist_ok=True)
        joblib.dump(
            self.clustering_model, os.path.join(path, "risk_profiler_clustering.pkl")
        )
        joblib.dump(self.scaler, os.path.join(path, "risk_profiler_scaler.pkl"))
        if self.pca is not None:
            joblib.dump(self.pca, os.path.join(path, "risk_profiler_pca.pkl"))
        model_data = {
            "config": self.config,
            "feature_names": self.feature_names,
            "profile_centers": (
                self.profile_centers.tolist()
                if self.profile_centers is not None
                else None
            ),
        }
        with open(os.path.join(path, "risk_profiler_data.json"), "w") as f:
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
        model : RiskProfiler
            Loaded model
        """
        with open(os.path.join(path, "risk_profiler_data.json"), "r") as f:
            model_data = json.load(f)
        instance = cls(model_data["config"])
        instance.feature_names = model_data["feature_names"]
        if model_data["profile_centers"] is not None:
            instance.profile_centers = np.array(model_data["profile_centers"])
        instance.clustering_model = joblib.load(
            os.path.join(path, "risk_profiler_clustering.pkl")
        )
        instance.scaler = joblib.load(os.path.join(path, "risk_profiler_scaler.pkl"))
        if os.path.exists(os.path.join(path, "risk_profiler_pca.pkl")):
            instance.pca = joblib.load(os.path.join(path, "risk_profiler_pca.pkl"))
        return instance


if __name__ == "__main__":
    np.random.seed(42)
    n_samples = 1000
    data = pd.DataFrame(
        {
            "age": np.random.randint(20, 80, n_samples),
            "income": np.random.randint(30000, 500000, n_samples),
            "net_worth": np.random.randint(10000, 5000000, n_samples),
            "investment_horizon": np.random.randint(1, 20, n_samples),
            "risk_tolerance": np.random.randint(1, 10, n_samples),
            "investment_knowledge": np.random.randint(1, 10, n_samples),
        }
    )
    profiler = RiskProfiler()
    profiler.fit(data)
    new_user = {
        "age": 35,
        "income": 120000,
        "net_worth": 350000,
        "investment_horizon": 15,
        "risk_tolerance": 7,
        "investment_knowledge": 6,
    }
    profile = profiler.predict(pd.DataFrame([new_user]))
    for feature, contribution in profile["feature_contributions"].items():
        logger.info(f"Feature: {feature}, Contribution: {contribution}")
    recommendations = profiler.get_profile_recommendations(profile["profile_id"])
    for strategy in recommendations["investment_strategies"]:
        logger.info(f"Strategy: {strategy['name']} - {strategy['description']}")
    questionnaire_responses = {
        "age": "30_to_40",
        "income": "100k_to_200k",
        "net_worth": "100k_to_500k",
        "investment_horizon": "more_than_10_years",
        "risk_tolerance": "high",
        "investment_knowledge": "intermediate",
    }
    questionnaire_profile = profiler.process_questionnaire(questionnaire_responses)
    fig1 = profiler.plot_profiles(data)
    fig2 = profiler.plot_asset_allocation()
    fig3 = profiler.plot_asset_allocation(
        profile_id=questionnaire_profile["profile_id"]
    )
    profiler.save("risk_profiler")
    loaded_profiler = RiskProfiler.load("risk_profiler")
    loaded_profile = loaded_profiler.predict(pd.DataFrame([new_user]))
