import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import json

class RiskProfiler:
    def __init__(self, config=None):
        """
        Initialize risk profiling system
        
        Parameters:
        -----------
        config : dict
            Configuration parameters for the model
        """
        self.config = {
            'num_profiles': 5,  # Number of risk profiles
            'profile_labels': ['Very Conservative', 'Conservative', 'Moderate', 'Aggressive', 'Very Aggressive'],
            'questionnaire_weights': {
                'age': 0.15,
                'income': 0.10,
                'net_worth': 0.15,
                'investment_horizon': 0.20,
                'risk_tolerance': 0.25,
                'investment_knowledge': 0.15
            },
            'clustering_method': 'kmeans',  # Currently only supports kmeans
            'random_state': 42  # Random seed
        }
        
        if config:
            self.config.update(config)
        
        self.scaler = StandardScaler()
        self.pca = None
        self.clustering_model = None
        self.profile_centers = None
        self.feature_names = None
        
    def _preprocess_data(self, data):
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
        # Store feature names
        self.feature_names = data.columns.tolist()
        
        # Scale data
        scaled_data = self.scaler.fit_transform(data)
        
        return scaled_data
    
    def _create_clustering_model(self):
        """
        Create clustering model
        
        Returns:
        --------
        model : sklearn.cluster.KMeans
            Clustering model
        """
        if self.config['clustering_method'] == 'kmeans':
            model = KMeans(
                n_clusters=self.config['num_profiles'],
                random_state=self.config['random_state']
            )
        else:
            raise ValueError(f"Unsupported clustering method: {self.config['clustering_method']}")
        
        return model
    
    def fit(self, data):
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
        # Preprocess data
        scaled_data = self._preprocess_data(data)
        
        # Create and fit clustering model
        self.clustering_model = self._create_clustering_model()
        self.clustering_model.fit(scaled_data)
        
        # Get cluster centers
        self.profile_centers = self.clustering_model.cluster_centers_
        
        # Apply PCA for visualization if more than 2 features
        if scaled_data.shape[1] > 2:
            self.pca = PCA(n_components=2)
            self.pca.fit(scaled_data)
        
        return self
    
    def predict(self, user_data):
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
        
        # Convert dict to DataFrame if needed
        if isinstance(user_data, dict):
            user_data = pd.DataFrame([user_data])
        
        # Ensure all required features are present
        missing_features = set(self.feature_names) - set(user_data.columns)
        if missing_features:
            raise ValueError(f"Missing features in user data: {missing_features}")
        
        # Reorder columns to match training data
        user_data = user_data[self.feature_names]
        
        # Scale user data
        scaled_user_data = self.scaler.transform(user_data)
        
        # Predict cluster
        cluster = self.clustering_model.predict(scaled_user_data)[0]
        
        # Get profile label
        profile_label = self.config['profile_labels'][cluster]
        
        # Calculate distance to cluster center
        center_distance = np.linalg.norm(scaled_user_data - self.profile_centers[cluster])
        
        # Calculate confidence score (inverse of normalized distance)
        max_distance = np.sqrt(len(self.feature_names))  # Maximum possible distance in scaled space
        confidence = max(0, 1 - (center_distance / max_distance))
        
        # Create profile dictionary
        profile = {
            'profile_id': int(cluster),
            'profile_label': profile_label,
            'confidence': float(confidence),
            'feature_contributions': self._calculate_feature_contributions(scaled_user_data[0], cluster)
        }
        
        return profile
    
    def _calculate_feature_contributions(self, user_features, cluster):
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
        # Get cluster center
        center = self.profile_centers[cluster]
        
        # Calculate absolute differences
        differences = np.abs(user_features - center)
        
        # Normalize differences
        total_difference = np.sum(differences)
        if total_difference > 0:
            contributions = 1 - (differences / total_difference)
        else:
            contributions = np.ones_like(differences)
        
        # Create dictionary
        return {feature: float(contrib) for feature, contrib in zip(self.feature_names, contributions)}
    
    def get_profile_recommendations(self, profile_id):
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
        
        if profile_id < 0 or profile_id >= self.config['num_profiles']:
            raise ValueError(f"Invalid profile ID: {profile_id}. Must be between 0 and {self.config['num_profiles']-1}.")
        
        # Define asset allocation based on risk profile
        asset_allocations = {
            0: {  # Very Conservative
                'stocks': 20,
                'bonds': 60,
                'cash': 15,
                'alternatives': 5
            },
            1: {  # Conservative
                'stocks': 35,
                'bonds': 50,
                'cash': 10,
                'alternatives': 5
            },
            2: {  # Moderate
                'stocks': 50,
                'bonds': 35,
                'cash': 5,
                'alternatives': 10
            },
            3: {  # Aggressive
                'stocks': 70,
                'bonds': 20,
                'cash': 0,
                'alternatives': 10
            },
            4: {  # Very Aggressive
                'stocks': 85,
                'bonds': 5,
                'cash': 0,
                'alternatives': 10
            }
        }
        
        # Define investment strategies
        investment_strategies = {
            0: [  # Very Conservative
                "Focus on capital preservation and income generation",
                "Invest in high-quality bonds and dividend-paying stocks",
                "Maintain higher cash reserves for stability",
                "Minimize exposure to market volatility"
            ],
            1: [  # Conservative
                "Balance between capital preservation and modest growth",
                "Diversify across fixed income and blue-chip stocks",
                "Maintain moderate cash reserves",
                "Consider inflation-protected securities"
            ],
            2: [  # Moderate
                "Balance between growth and income",
                "Diversify across domestic and international markets",
                "Consider both value and growth investments",
                "Maintain small cash position for opportunities"
            ],
            3: [  # Aggressive
                "Focus on long-term capital appreciation",
                "Overweight growth stocks and emerging markets",
                "Consider alternative investments for diversification",
                "Accept higher volatility for potential higher returns"
            ],
            4: [  # Very Aggressive
                "Maximize long-term growth potential",
                "Invest in high-growth sectors and emerging markets",
                "Consider leveraged positions and concentrated bets",
                "Accept significant volatility for maximum return potential"
            ]
        }
        
        # Define recommended investment vehicles
        investment_vehicles = {
            0: [  # Very Conservative
                "Treasury bonds and notes",
                "Municipal bonds",
                "High-quality corporate bonds",
                "Certificates of deposit",
                "Money market funds",
                "Dividend aristocrat stocks"
            ],
            1: [  # Conservative
                "Investment-grade corporate bonds",
                "Government bonds",
                "Blue-chip dividend stocks",
                "High-yield savings accounts",
                "Balanced mutual funds",
                "REITs for income"
            ],
            2: [  # Moderate
                "Diversified stock index funds",
                "Balanced ETFs",
                "Corporate and government bonds",
                "International developed market funds",
                "Select REITs and preferred stocks",
                "Target-date funds"
            ],
            3: [  # Aggressive
                "Growth stock funds",
                "Small and mid-cap stock funds",
                "Emerging market funds",
                "High-yield bonds",
                "Commodities",
                "Select alternative investments"
            ],
            4: [  # Very Aggressive
                "Aggressive growth stocks",
                "Sector-specific funds (technology, biotech)",
                "Emerging market stocks",
                "Private equity",
                "Cryptocurrency allocation",
                "Leveraged ETFs"
            ]
        }
        
        # Create recommendations dictionary
        recommendations = {
            'profile_id': profile_id,
            'profile_label': self.config['profile_labels'][profile_id],
            'asset_allocation': asset_allocations[profile_id],
            'investment_strategies': investment_strategies[profile_id],
            'recommended_vehicles': investment_vehicles[profile_id],
            'risk_metrics': {
                'expected_annual_return': 2 + (profile_id * 2),  # Simplified estimate
                'expected_volatility': 2 + (profile_id * 3),  # Simplified estimate
                'max_drawdown': 5 + (profile_id * 5),  # Simplified estimate
                'investment_horizon': 1 + (profile_id * 2)  # Years
            }
        }
        
        return recommendations
    
    def process_questionnaire(self, responses):
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
        # Define scoring for each question
        scoring = {
            'age': {
                'under_30': 5,
                '30_to_40': 4,
                '41_to_50': 3,
                '51_to_60': 2,
                'over_60': 1
            },
            'income': {
                'under_50k': 1,
                '50k_to_100k': 2,
                '100k_to_200k': 3,
                '200k_to_500k': 4,
                'over_500k': 5
            },
            'net_worth': {
                'under_100k': 1,
                '100k_to_500k': 2,
                '500k_to_1m': 3,
                '1m_to_5m': 4,
                'over_5m': 5
            },
            'investment_horizon': {
                'less_than_1_year': 1,
                '1_to_3_years': 2,
                '3_to_5_years': 3,
                '5_to_10_years': 4,
                'more_than_10_years': 5
            },
            'risk_tolerance': {
                'very_low': 1,
                'low': 2,
                'medium': 3,
                'high': 4,
                'very_high': 5
            },
            'investment_knowledge': {
                'novice': 1,
                'basic': 2,
                'intermediate': 3,
                'advanced': 4,
                'expert': 5
            }
        }
        
        # Calculate scores
        scores = {}
        for category, response in responses.items():
            if category in scoring and response in scoring[category]:
                scores[category] = scoring[category][response]
            else:
                raise ValueError(f"Invalid response '{response}' for category '{category}'")
        
        # Calculate weighted score
        weighted_score = 0
        for category, score in scores.items():
            if category in self.config['questionnaire_weights']:
                weighted_score += score * self.config['questionnaire_weights'][category]
        
        # Normalize to 0-1 range
        normalized_score = (weighted_score - 1) / 4  # Min score is 1, max is 5
        
        # Map to profile
        profile_id = min(int(normalized_score * self.config['num_profiles']), self.config['num_profiles'] - 1)
        
        # Get profile label
        profile_label = self.config['profile_labels'][profile_id]
        
        # Create profile dictionary
        profile = {
            'profile_id': profile_id,
            'profile_label': profile_label,
            'score': weighted_score,
            'normalized_score': normalized_score,
            'category_scores': scores,
            'recommendations': self.get_profile_recommendations(profile_id)
        }
        
        return profile
    
    def plot_profiles(self, data=None, figsize=(12, 10)):
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
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # If data is provided, plot user points
        if data is not None:
            # Scale data
            scaled_data = self.scaler.transform(data[self.feature_names])
            
            # Predict clusters
            clusters = self.clustering_model.predict(scaled_data)
            
            # Apply PCA if needed
            if self.pca is not None:
                points = self.pca.transform(scaled_data)
                centers = self.pca.transform(self.profile_centers)
            else:
                points = scaled_data
                centers = self.profile_centers
            
            # Plot points (first two dimensions only)
            for i in range(self.config['num_profiles']):
                mask = clusters == i
                ax.scatter(
                    points[mask, 0],
                    points[mask, 1],
                    alpha=0.7,
                    s=50,
                    label=f"Profile {i+1}: {self.config['profile_labels'][i]}"
                )
        
            # Plot cluster centers
            ax.scatter(
                centers[:, 0],
                centers[:, 1],
                s=200,
                c='red',
                marker='X',
                label='Profile Centers'
            )
        else:
            # Just plot cluster centers
            if self.pca is not None:
                centers = self.pca.transform(self.profile_centers)
            else:
                centers = self.profile_centers
            
            # Plot cluster centers
            for i in range(self.config['num_profiles']):
                ax.scatter(
                    centers[i, 0],
                    centers[i, 1],
                    s=200,
                    marker='X',
                    label=f"Profile {i+1}: {self.config['profile_labels'][i]}"
                )
        
        # Add labels and title
        if self.pca is not None:
            ax.set_xlabel(f"Principal Component 1")
            ax.set_ylabel(f"Principal Component 2")
        else:
            ax.set_xlabel(self.feature_names[0])
            ax.set_ylabel(self.feature_names[1])
        
        ax.set_title('Risk Profiles')
        
        # Add legend
        ax.legend()
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def plot_asset_allocation(self, profile_id=None, figsize=(10, 8)):
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
        # Define asset allocation based on risk profile
        asset_allocations = {
            0: {  # Very Conservative
                'stocks': 20,
                'bonds': 60,
                'cash': 15,
                'alternatives': 5
            },
            1: {  # Conservative
                'stocks': 35,
                'bonds': 50,
                'cash': 10,
                'alternatives': 5
            },
            2: {  # Moderate
                'stocks': 50,
                'bonds': 35,
                'cash': 5,
                'alternatives': 10
            },
            3: {  # Aggressive
                'stocks': 70,
                'bonds': 20,
                'cash': 0,
                'alternatives': 10
            },
            4: {  # Very Aggressive
                'stocks': 85,
                'bonds': 5,
                'cash': 0,
                'alternatives': 10
            }
        }
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        if profile_id is not None:
            # Plot single profile
            if profile_id < 0 or profile_id >= self.config['num_profiles']:
                raise ValueError(f"Invalid profile ID: {profile_id}. Must be between 0 and {self.config['num_profiles']-1}.")
            
            allocation = asset_allocations[profile_id]
            
            # Create pie chart
            ax.pie(
                allocation.values(),
                labels=allocation.keys(),
                autopct='%1.1f%%',
                startangle=90,
                colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            )
            
            ax.set_title(f"Asset Allocation for {self.config['profile_labels'][profile_id]} Profile")
        else:
            # Plot all profiles
            profiles = list(range(self.config['num_profiles']))
            assets = list(asset_allocations[0].keys())
            
            # Create grouped bar chart
            x = np.arange(len(profiles))
            width = 0.2
            multiplier = 0
            
            for asset in assets:
                asset_values = [asset_allocations[p][asset] for p in profiles]
                offset = width * multiplier
                rects = ax.bar(x + offset, asset_values, width, label=asset.capitalize())
                ax.bar_label(rects, padding=3)
                multiplier += 1
            
            # Add labels and title
            ax.set_xlabel('Risk Profile')
            ax.set_ylabel('Allocation (%)')
            ax.set_title('Asset Allocation by Risk Profile')
            ax.set_xticks(x + width * (len(assets) - 1) / 2)
            ax.set_xticklabels(self.config['profile_labels'])
            ax.legend(loc='upper left')
            
            # Add grid
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def save(self, path):
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
        
        # Save clustering model
        joblib.dump(self.clustering_model, os.path.join(path, 'risk_profiler_clustering.pkl'))
        
        # Save scaler
        joblib.dump(self.scaler, os.path.join(path, 'risk_profiler_scaler.pkl'))
        
        # Save PCA if exists
        if self.pca is not None:
            joblib.dump(self.pca, os.path.join(path, 'risk_profiler_pca.pkl'))
        
        # Save config and other attributes
        model_data = {
            'config': self.config,
            'feature_names': self.feature_names,
            'profile_centers': self.profile_centers.tolist() if self.profile_centers is not None else None
        }
        
        with open(os.path.join(path, 'risk_profiler_data.json'), 'w') as f:
            json.dump(model_data, f)
    
    @classmethod
    def load(cls, path):
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
        # Load model data
        with open(os.path.join(path, 'risk_profiler_data.json'), 'r') as f:
            model_data = json.load(f)
        
        # Create instance
        instance = cls(model_data['config'])
        instance.feature_names = model_data['feature_names']
        
        if model_data['profile_centers'] is not None:
            instance.profile_centers = np.array(model_data['profile_centers'])
        
        # Load clustering model
        instance.clustering_model = joblib.load(os.path.join(path, 'risk_profiler_clustering.pkl'))
        
        # Load scaler
        instance.scaler = joblib.load(os.path.join(path, 'risk_profiler_scaler.pkl'))
        
        # Load PCA if exists
        if os.path.exists(os.path.join(path, 'risk_profiler_pca.pkl')):
            instance.pca = joblib.load(os.path.join(path, 'risk_profiler_pca.pkl'))
        
        return instance

# Example usage
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    
    # Create synthetic user data
    data = pd.DataFrame({
        'age': np.random.randint(20, 80, n_samples),
        'income': np.random.randint(30000, 500000, n_samples),
        'net_worth': np.random.randint(10000, 5000000, n_samples),
        'investment_horizon': np.random.randint(1, 20, n_samples),
        'risk_tolerance': np.random.randint(1, 10, n_samples),
        'investment_knowledge': np.random.randint(1, 10, n_samples)
    })
    
    # Initialize and fit risk profiler
    profiler = RiskProfiler()
    profiler.fit(data)
    
    # Create a new user
    new_user = {
        'age': 35,
        'income': 120000,
        'net_worth': 350000,
        'investment_horizon': 15,
        'risk_tolerance': 7,
        'investment_knowledge': 6
    }
    
    # Predict risk profile
    profile = profiler.predict(pd.DataFrame([new_user]))
    print("Risk Profile:")
    print(f"Profile: {profile['profile_label']} (ID: {profile['profile_id']})")
    print(f"Confidence: {profile['confidence']:.2f}")
    print("\nFeature Contributions:")
    for feature, contribution in profile['feature_contributions'].items():
        print(f"{feature}: {contribution:.2f}")
    
    # Get profile recommendations
    recommendations = profiler.get_profile_recommendations(profile['profile_id'])
    print("\nRecommendations:")
    print(f"Asset Allocation: {recommendations['asset_allocation']}")
    print("\nInvestment Strategies:")
    for strategy in recommendations['investment_strategies']:
        print(f"- {strategy}")
    
    # Process questionnaire
    questionnaire_responses = {
        'age': '30_to_40',
        'income': '100k_to_200k',
        'net_worth': '100k_to_500k',
        'investment_horizon': 'more_than_10_years',
        'risk_tolerance': 'high',
        'investment_knowledge': 'intermediate'
    }
    
    questionnaire_profile = profiler.process_questionnaire(questionnaire_responses)
    print("\nQuestionnaire Profile:")
    print(f"Profile: {questionnaire_profile['profile_label']} (ID: {questionnaire_profile['profile_id']})")
    print(f"Score: {questionnaire_profile['score']:.2f}")
    
    # Plot profiles
    fig1 = profiler.plot_profiles(data)
    
    # Plot asset allocation
    fig2 = profiler.plot_asset_allocation()
    fig3 = profiler.plot_asset_allocation(profile_id=questionnaire_profile['profile_id'])
    
    # Save model
    profiler.save('risk_profiler')
    
    # Load model
    loaded_profiler = RiskProfiler.load('risk_profiler')
    
    # Verify loaded model
    loaded_profile = loaded_profiler.predict(pd.DataFrame([new_user]))
    print("\nLoaded Model Profile:")
    print(f"Profile: {loaded_profile['profile_label']} (ID: {loaded_profile['profile_id']})")
    print(f"Confidence: {loaded_profile['confidence']:.2f}")
