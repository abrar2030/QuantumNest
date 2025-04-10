import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import joblib
import os
import json

class PCAAnalyzer:
    def __init__(self, config=None):
        """
        Initialize PCA model for market analysis
        
        Parameters:
        -----------
        config : dict
            Configuration parameters for the model
        """
        self.config = {
            'n_components': 3,  # Number of principal components
            'explained_variance_threshold': 0.8,  # Minimum explained variance threshold
            'standardize': True,  # Whether to standardize features
            'random_state': 42  # Random seed
        }
        
        if config:
            self.config.update(config)
        
        self.pca = None
        self.scaler = None
        self.feature_names = None
        self.explained_variance_ratio_ = None
        self.components_ = None
        
    def fit(self, data, features=None):
        """
        Fit PCA model to data
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Input data
        features : list
            List of feature columns to use (if None, use all numeric columns)
            
        Returns:
        --------
        self : PCAAnalyzer
            Fitted model
        """
        # Select features
        if features is None:
            # Use all numeric columns
            features = data.select_dtypes(include=[np.number]).columns.tolist()
        
        self.feature_names = features
        X = data[features].values
        
        # Standardize features if specified
        if self.config['standardize']:
            self.scaler = StandardScaler()
            X = self.scaler.fit_transform(X)
        
        # Determine number of components
        if self.config['n_components'] == 'auto':
            # Fit PCA with all components
            temp_pca = PCA(random_state=self.config['random_state'])
            temp_pca.fit(X)
            
            # Find number of components that explain desired variance
            cumulative_variance = np.cumsum(temp_pca.explained_variance_ratio_)
            n_components = np.argmax(cumulative_variance >= self.config['explained_variance_threshold']) + 1
            
            # Update config
            self.config['n_components'] = n_components
        
        # Fit PCA
        self.pca = PCA(n_components=self.config['n_components'], random_state=self.config['random_state'])
        self.pca.fit(X)
        
        # Store explained variance and components
        self.explained_variance_ratio_ = self.pca.explained_variance_ratio_
        self.components_ = self.pca.components_
        
        return self
    
    def transform(self, data):
        """
        Transform data using fitted PCA model
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Input data
            
        Returns:
        --------
        transformed : pandas.DataFrame
            Transformed data
        """
        if self.pca is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        # Extract features
        X = data[self.feature_names].values
        
        # Standardize if needed
        if self.config['standardize']:
            X = self.scaler.transform(X)
        
        # Transform data
        transformed = self.pca.transform(X)
        
        # Create DataFrame
        columns = [f"PC{i+1}" for i in range(self.config['n_components'])]
        transformed_df = pd.DataFrame(transformed, index=data.index, columns=columns)
        
        return transformed_df
    
    def fit_transform(self, data, features=None):
        """
        Fit PCA model and transform data
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Input data
        features : list
            List of feature columns to use (if None, use all numeric columns)
            
        Returns:
        --------
        transformed : pandas.DataFrame
            Transformed data
        """
        self.fit(data, features)
        return self.transform(data)
    
    def get_feature_importance(self):
        """
        Get feature importance based on PCA loadings
        
        Returns:
        --------
        importance : pandas.DataFrame
            Feature importance for each principal component
        """
        if self.pca is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        # Create DataFrame with loadings
        loadings = pd.DataFrame(
            self.pca.components_.T,
            index=self.feature_names,
            columns=[f"PC{i+1}" for i in range(self.config['n_components'])]
        )
        
        # Calculate absolute loadings for importance
        abs_loadings = loadings.abs()
        
        # Calculate overall importance as weighted sum of loadings
        importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': np.average(abs_loadings.values, axis=1, weights=self.explained_variance_ratio_)
        }).sort_values('importance', ascending=False)
        
        return importance
    
    def get_explained_variance(self):
        """
        Get explained variance information
        
        Returns:
        --------
        variance_info : dict
            Explained variance information
        """
        if self.pca is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        variance_info = {
            'explained_variance_ratio': self.explained_variance_ratio_.tolist(),
            'cumulative_variance': np.cumsum(self.explained_variance_ratio_).tolist(),
            'total_explained_variance': sum(self.explained_variance_ratio_)
        }
        
        return variance_info
    
    def plot_explained_variance(self, figsize=(10, 6)):
        """
        Plot explained variance
        
        Parameters:
        -----------
        figsize : tuple
            Figure size
            
        Returns:
        --------
        fig : matplotlib.figure.Figure
            Figure object
        """
        if self.pca is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Individual explained variance
        ax.bar(
            range(1, len(self.explained_variance_ratio_) + 1),
            self.explained_variance_ratio_,
            alpha=0.7,
            label='Individual explained variance'
        )
        
        # Cumulative explained variance
        ax.step(
            range(1, len(self.explained_variance_ratio_) + 1),
            np.cumsum(self.explained_variance_ratio_),
            where='mid',
            label='Cumulative explained variance',
            color='red'
        )
        
        ax.set_xlabel('Principal Components')
        ax.set_ylabel('Explained Variance Ratio')
        ax.set_title('Explained Variance by Principal Components')
        ax.set_xticks(range(1, len(self.explained_variance_ratio_) + 1))
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def plot_feature_importance(self, n_features=10, figsize=(12, 8)):
        """
        Plot feature importance
        
        Parameters:
        -----------
        n_features : int
            Number of top features to show
        figsize : tuple
            Figure size
            
        Returns:
        --------
        fig : matplotlib.figure.Figure
            Figure object
        """
        if self.pca is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        importance = self.get_feature_importance()
        top_features = importance.head(n_features)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.barh(
            top_features['feature'],
            top_features['importance'],
            color='skyblue'
        )
        
        ax.set_xlabel('Importance')
        ax.set_ylabel('Features')
        ax.set_title(f'Top {n_features} Feature Importance')
        ax.invert_yaxis()  # Display the highest importance at the top
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def plot_biplot(self, transformed_data, features_to_show=5, figsize=(12, 10)):
        """
        Create a biplot of the first two principal components
        
        Parameters:
        -----------
        transformed_data : pandas.DataFrame
            Transformed data from transform() method
        features_to_show : int
            Number of top features to show in the biplot
        figsize : tuple
            Figure size
            
        Returns:
        --------
        fig : matplotlib.figure.Figure
            Figure object
        """
        if self.pca is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        # Get top features
        importance = self.get_feature_importance()
        top_features = importance.head(features_to_show)['feature'].tolist()
        
        # Get indices of top features
        top_indices = [self.feature_names.index(feature) for feature in top_features]
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot transformed data points
        ax.scatter(
            transformed_data['PC1'],
            transformed_data['PC2'],
            alpha=0.7,
            s=30
        )
        
        # Plot feature vectors
        for i in top_indices:
            ax.arrow(
                0, 0,
                self.components_[0, i] * 1.5,
                self.components_[1, i] * 1.5,
                head_width=0.05,
                head_length=0.05,
                fc='red',
                ec='red'
            )
            ax.text(
                self.components_[0, i] * 1.7,
                self.components_[1, i] * 1.7,
                self.feature_names[i],
                color='red',
                ha='center',
                va='center'
            )
        
        # Add circle
        circle = plt.Circle((0, 0), 1, fill=False, linestyle='--', color='gray')
        ax.add_patch(circle)
        
        # Set labels and title
        ax.set_xlabel(f'PC1 ({self.explained_variance_ratio_[0]:.2%} explained variance)')
        ax.set_ylabel(f'PC2 ({self.explained_variance_ratio_[1]:.2%} explained variance)')
        ax.set_title('PCA Biplot')
        
        # Set equal aspect ratio
        ax.set_aspect('equal')
        
        # Set limits
        limit = 1.2
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
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
        if self.pca is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        os.makedirs(path, exist_ok=True)
        
        # Save PCA model
        joblib.dump(self.pca, os.path.join(path, 'pca_model.pkl'))
        
        # Save scaler if exists
        if self.scaler is not None:
            joblib.dump(self.scaler, os.path.join(path, 'pca_scaler.pkl'))
        
        # Save config and feature names
        with open(os.path.join(path, 'pca_config.json'), 'w') as f:
            json.dump({
                'config': self.config,
                'feature_names': self.feature_names,
                'explained_variance_ratio': self.explained_variance_ratio_.tolist() if self.explained_variance_ratio_ is not None else None
            }, f)
    
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
        model : PCAAnalyzer
            Loaded model
        """
        # Load config and feature names
        with open(os.path.join(path, 'pca_config.json'), 'r') as f:
            data = json.load(f)
        
        # Create instance
        instance = cls(data['config'])
        instance.feature_names = data['feature_names']
        
        # Load PCA model
        instance.pca = joblib.load(os.path.join(path, 'pca_model.pkl'))
        
        # Load scaler if exists
        if os.path.exists(os.path.join(path, 'pca_scaler.pkl')):
            instance.scaler = joblib.load(os.path.join(path, 'pca_scaler.pkl'))
        
        # Set explained variance and components
        instance.explained_variance_ratio_ = np.array(data['explained_variance_ratio']) if data['explained_variance_ratio'] is not None else None
        instance.components_ = instance.pca.components_
        
        return instance

# Example usage
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    # Create correlated features
    X = np.random.randn(n_samples, 3)
    X1 = X[:, 0] + np.random.randn(n_samples) * 0.1
    X2 = X[:, 0] + X[:, 1] + np.random.randn(n_samples) * 0.1
    X3 = X[:, 1] + np.random.randn(n_samples) * 0.1
    X4 = X[:, 1] + X[:, 2] + np.random.randn(n_samples) * 0.1
    X5 = X[:, 2] + np.random.randn(n_samples) * 0.1
    
    # Add some random features
    X6 = np.random.randn(n_samples)
    X7 = np.random.randn(n_samples)
    X8 = np.random.randn(n_samples)
    X9 = np.random.randn(n_samples)
    X10 = np.random.randn(n_samples)
    
    # Create DataFrame
    data = pd.DataFrame({
        'feature1': X1,
        'feature2': X2,
        'feature3': X3,
        'feature4': X4,
        'feature5': X5,
        'feature6': X6,
        'feature7': X7,
        'feature8': X8,
        'feature9': X9,
        'feature10': X10
    })
    
    # Initialize and fit PCA model
    pca_analyzer = PCAAnalyzer({'n_components': 'auto', 'explained_variance_threshold': 0.8})
    transformed_data = pca_analyzer.fit_transform(data)
    
    print("Transformed data shape:", transformed_data.shape)
    print("Explained variance ratio:", pca_analyzer.explained_variance_ratio_)
    print("Total explained variance:", sum(pca_analyzer.explained_variance_ratio_))
    
    # Get feature importance
    importance = pca_analyzer.get_feature_importance()
    print("\nFeature importance:")
    print(importance.head(5))
    
    # Plot explained variance
    fig1 = pca_analyzer.plot_explained_variance()
    
    # Plot feature importance
    fig2 = pca_analyzer.plot_feature_importance()
    
    # Plot biplot
    fig3 = pca_analyzer.plot_biplot(transformed_data)
    
    # Save model
    pca_analyzer.save('pca_model')
    
    # Load model
    loaded_pca = PCAAnalyzer.load('pca_model')
    
    # Transform new data
    new_transformed = loaded_pca.transform(data.head(10))
    print("\nTransformed new data:")
    print(new_transformed.head())
