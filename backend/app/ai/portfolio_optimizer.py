import numpy as np
import pandas as pd
import scipy.optimize as sco
import matplotlib.pyplot as plt
import joblib
import os
import json

class PortfolioOptimizer:
    def __init__(self, config=None):
        """
        Initialize portfolio optimization model
        
        Parameters:
        -----------
        config : dict
            Configuration parameters for the model
        """
        self.config = {
            'risk_free_rate': 0.02,  # Annual risk-free rate
            'optimization_method': 'efficient_frontier',  # Options: 'efficient_frontier', 'max_sharpe', 'min_volatility', 'risk_parity'
            'target_return': None,  # Target return for efficient frontier optimization
            'target_risk': None,  # Target risk for efficient frontier optimization
            'constraints': {
                'min_weight': 0.0,  # Minimum weight per asset
                'max_weight': 1.0,  # Maximum weight per asset
            },
            'rebalance_frequency': 'quarterly',  # Options: 'monthly', 'quarterly', 'semi_annually', 'annually'
            'random_state': 42  # Random seed
        }
        
        if config:
            self.config.update(config)
        
        self.returns = None
        self.cov_matrix = None
        self.assets = None
        self.optimal_weights = None
        self.optimization_result = None
        
    def _calculate_portfolio_performance(self, weights):
        """
        Calculate portfolio performance metrics
        
        Parameters:
        -----------
        weights : numpy.ndarray
            Asset weights
            
        Returns:
        --------
        performance : dict
            Portfolio performance metrics
        """
        # Calculate expected portfolio return
        portfolio_return = np.sum(self.returns.mean() * weights) * 252  # Annualized
        
        # Calculate portfolio volatility
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix * 252, weights)))
        
        # Calculate Sharpe ratio
        sharpe_ratio = (portfolio_return - self.config['risk_free_rate']) / portfolio_volatility
        
        return {
            'return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
        }
    
    def _negative_sharpe_ratio(self, weights):
        """
        Calculate negative Sharpe ratio for optimization
        
        Parameters:
        -----------
        weights : numpy.ndarray
            Asset weights
            
        Returns:
        --------
        negative_sharpe : float
            Negative Sharpe ratio
        """
        performance = self._calculate_portfolio_performance(weights)
        return -performance['sharpe_ratio']
    
    def _portfolio_volatility(self, weights):
        """
        Calculate portfolio volatility for optimization
        
        Parameters:
        -----------
        weights : numpy.ndarray
            Asset weights
            
        Returns:
        --------
        volatility : float
            Portfolio volatility
        """
        return self._calculate_portfolio_performance(weights)['volatility']
    
    def _portfolio_return(self, weights):
        """
        Calculate portfolio return for optimization
        
        Parameters:
        -----------
        weights : numpy.ndarray
            Asset weights
            
        Returns:
        --------
        returns : float
            Portfolio return
        """
        return self._calculate_portfolio_performance(weights)['return']
    
    def _optimize_max_sharpe(self):
        """
        Optimize portfolio for maximum Sharpe ratio
        
        Returns:
        --------
        result : dict
            Optimization result
        """
        num_assets = len(self.assets)
        args = ()
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((self.config['constraints']['min_weight'], self.config['constraints']['max_weight']) for _ in range(num_assets))
        initial_weights = np.array([1.0 / num_assets] * num_assets)
        
        result = sco.minimize(
            self._negative_sharpe_ratio,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            args=args
        )
        
        return {
            'weights': result['x'],
            'sharpe_ratio': -result['fun'],
            'success': result['success'],
            'message': result['message']
        }
    
    def _optimize_min_volatility(self):
        """
        Optimize portfolio for minimum volatility
        
        Returns:
        --------
        result : dict
            Optimization result
        """
        num_assets = len(self.assets)
        args = ()
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((self.config['constraints']['min_weight'], self.config['constraints']['max_weight']) for _ in range(num_assets))
        initial_weights = np.array([1.0 / num_assets] * num_assets)
        
        result = sco.minimize(
            self._portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            args=args
        )
        
        return {
            'weights': result['x'],
            'volatility': result['fun'],
            'success': result['success'],
            'message': result['message']
        }
    
    def _optimize_efficient_frontier(self):
        """
        Optimize portfolio for efficient frontier
        
        Returns:
        --------
        result : dict
            Optimization result
        """
        num_assets = len(self.assets)
        args = ()
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        
        # Add target return constraint if specified
        if self.config['target_return'] is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: self._portfolio_return(x) - self.config['target_return']
            })
        
        # Add target risk constraint if specified
        if self.config['target_risk'] is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: self._portfolio_volatility(x) - self.config['target_risk']
            })
        
        bounds = tuple((self.config['constraints']['min_weight'], self.config['constraints']['max_weight']) for _ in range(num_assets))
        initial_weights = np.array([1.0 / num_assets] * num_assets)
        
        # If both target return and risk are None, optimize for max Sharpe ratio
        if self.config['target_return'] is None and self.config['target_risk'] is None:
            return self._optimize_max_sharpe()
        
        # If target return is specified but not risk, minimize volatility
        if self.config['target_return'] is not None and self.config['target_risk'] is None:
            result = sco.minimize(
                self._portfolio_volatility,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                args=args
            )
            
            return {
                'weights': result['x'],
                'volatility': result['fun'],
                'return': self.config['target_return'],
                'success': result['success'],
                'message': result['message']
            }
        
        # If target risk is specified but not return, maximize return
        if self.config['target_risk'] is not None and self.config['target_return'] is None:
            result = sco.minimize(
                lambda x: -self._portfolio_return(x),
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                args=args
            )
            
            return {
                'weights': result['x'],
                'volatility': self.config['target_risk'],
                'return': -result['fun'],
                'success': result['success'],
                'message': result['message']
            }
        
        # If both are specified, minimize volatility (constraints will handle the rest)
        result = sco.minimize(
            self._portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            args=args
        )
        
        return {
            'weights': result['x'],
            'volatility': result['fun'],
            'return': self.config['target_return'],
            'success': result['success'],
            'message': result['message']
        }
    
    def _optimize_risk_parity(self):
        """
        Optimize portfolio for risk parity
        
        Returns:
        --------
        result : dict
            Optimization result
        """
        num_assets = len(self.assets)
        
        def risk_contribution(weights):
            portfolio_volatility = self._portfolio_volatility(weights)
            marginal_contribution = np.dot(self.cov_matrix * 252, weights)
            risk_contribution = np.multiply(marginal_contribution, weights) / portfolio_volatility
            return risk_contribution
        
        def risk_parity_objective(weights):
            target_risk = 1.0 / num_assets
            asset_risk_contribution = risk_contribution(weights)
            return np.sum((asset_risk_contribution - target_risk)**2)
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        bounds = tuple((self.config['constraints']['min_weight'], self.config['constraints']['max_weight']) for _ in range(num_assets))
        initial_weights = np.array([1.0 / num_assets] * num_assets)
        
        result = sco.minimize(
            risk_parity_objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return {
            'weights': result['x'],
            'risk_parity_score': result['fun'],
            'success': result['success'],
            'message': result['message']
        }
    
    def optimize(self, returns_data):
        """
        Optimize portfolio based on historical returns
        
        Parameters:
        -----------
        returns_data : pandas.DataFrame
            Historical returns data with assets as columns
            
        Returns:
        --------
        result : dict
            Optimization result
        """
        # Store returns data
        self.returns = returns_data
        self.assets = returns_data.columns.tolist()
        
        # Calculate covariance matrix
        self.cov_matrix = returns_data.cov()
        
        # Perform optimization based on method
        if self.config['optimization_method'] == 'max_sharpe':
            result = self._optimize_max_sharpe()
        elif self.config['optimization_method'] == 'min_volatility':
            result = self._optimize_min_volatility()
        elif self.config['optimization_method'] == 'risk_parity':
            result = self._optimize_risk_parity()
        else:  # Default to efficient frontier
            result = self._optimize_efficient_frontier()
        
        # Store optimal weights
        self.optimal_weights = result['weights']
        
        # Calculate portfolio performance
        performance = self._calculate_portfolio_performance(self.optimal_weights)
        
        # Create result dictionary
        self.optimization_result = {
            'weights': {asset: weight for asset, weight in zip(self.assets, self.optimal_weights)},
            'performance': performance,
            'optimization_details': result
        }
        
        return self.optimization_result
    
    def generate_efficient_frontier(self, returns_data, num_portfolios=100):
        """
        Generate efficient frontier
        
        Parameters:
        -----------
        returns_data : pandas.DataFrame
            Historical returns data with assets as columns
        num_portfolios : int
            Number of portfolios to generate
            
        Returns:
        --------
        efficient_frontier : pandas.DataFrame
            Efficient frontier data
        """
        # Store returns data
        self.returns = returns_data
        self.assets = returns_data.columns.tolist()
        
        # Calculate covariance matrix
        self.cov_matrix = returns_data.cov()
        
        # Generate random portfolios
        num_assets = len(self.assets)
        results = []
        
        np.random.seed(self.config['random_state'])
        
        for _ in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            
            # Ensure weights are within constraints
            weights = np.clip(
                weights,
                self.config['constraints']['min_weight'],
                self.config['constraints']['max_weight']
            )
            weights /= np.sum(weights)
            
            performance = self._calculate_portfolio_performance(weights)
            
            results.append({
                'return': performance['return'],
                'volatility': performance['volatility'],
                'sharpe_ratio': performance['sharpe_ratio'],
                'weights': weights
            })
        
        # Convert to DataFrame
        efficient_frontier = pd.DataFrame(results)
        
        # Find optimal portfolios
        max_sharpe_idx = efficient_frontier['sharpe_ratio'].idxmax()
        min_vol_idx = efficient_frontier['volatility'].idxmin()
        
        # Add asset weights to DataFrame
        for i, asset in enumerate(self.assets):
            efficient_frontier[f'weight_{asset}'] = efficient_frontier['weights'].apply(lambda x: x[i])
        
        # Add optimal portfolio indicators
        efficient_frontier['is_max_sharpe'] = False
        efficient_frontier.loc[max_sharpe_idx, 'is_max_sharpe'] = True
        
        efficient_frontier['is_min_volatility'] = False
        efficient_frontier.loc[min_vol_idx, 'is_min_volatility'] = True
        
        # Drop weights column (now expanded to individual columns)
        efficient_frontier = efficient_frontier.drop('weights', axis=1)
        
        return efficient_frontier
    
    def plot_efficient_frontier(self, efficient_frontier, figsize=(12, 8)):
        """
        Plot efficient frontier
        
        Parameters:
        -----------
        efficient_frontier : pandas.DataFrame
            Efficient frontier data from generate_efficient_frontier method
        figsize : tuple
            Figure size
            
        Returns:
        --------
        fig : matplotlib.figure.Figure
            Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot random portfolios
        scatter = ax.scatter(
            efficient_frontier['volatility'],
            efficient_frontier['return'],
            c=efficient_frontier['sharpe_ratio'],
            cmap='viridis',
            alpha=0.7,
            s=30
        )
        
        # Highlight max Sharpe ratio portfolio
        max_sharpe_portfolio = efficient_frontier.loc[efficient_frontier['is_max_sharpe']]
        ax.scatter(
            max_sharpe_portfolio['volatility'],
            max_sharpe_portfolio['return'],
            marker='*',
            color='red',
            s=300,
            label='Max Sharpe Ratio'
        )
        
        # Highlight min volatility portfolio
        min_vol_portfolio = efficient_frontier.loc[efficient_frontier['is_min_volatility']]
        ax.scatter(
            min_vol_portfolio['volatility'],
            min_vol_portfolio['return'],
            marker='P',
            color='green',
            s=200,
            label='Min Volatility'
        )
        
        # Highlight current portfolio if available
        if self.optimal_weights is not None:
            current_performance = self._calculate_portfolio_performance(self.optimal_weights)
            ax.scatter(
                current_performance['volatility'],
                current_performance['return'],
                marker='X',
                color='blue',
                s=200,
                label='Current Portfolio'
            )
        
        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Sharpe Ratio')
        
        # Add labels and title
        ax.set_xlabel('Volatility (Annualized)')
        ax.set_ylabel('Return (Annualized)')
        ax.set_title('Efficient Frontier')
        
        # Add legend
        ax.legend()
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def plot_asset_allocation(self, figsize=(10, 6)):
        """
        Plot asset allocation
        
        Parameters:
        -----------
        figsize : tuple
            Figure size
            
        Returns:
        --------
        fig : matplotlib.figure.Figure
            Figure object
        """
        if self.optimal_weights is None:
            raise ValueError("No optimal weights available. Call optimize() first.")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Sort weights for better visualization
        sorted_indices = np.argsort(self.optimal_weights)[::-1]
        sorted_assets = [self.assets[i] for i in sorted_indices]
        sorted_weights = self.optimal_weights[sorted_indices]
        
        # Plot horizontal bar chart
        ax.barh(sorted_assets, sorted_weights, color='skyblue')
        
        # Add labels and title
        ax.set_xlabel('Weight')
        ax.set_ylabel('Asset')
        ax.set_title('Optimal Asset Allocation')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add weight values as text
        for i, weight in enumerate(sorted_weights):
            ax.text(weight + 0.01, i, f'{weight:.2%}', va='center')
        
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
        os.makedirs(path, exist_ok=True)
        
        # Save model data
        model_data = {
            'config': self.config,
            'assets': self.assets,
            'optimal_weights': self.optimal_weights.tolist() if self.optimal_weights is not None else None,
            'optimization_result': self.optimization_result
        }
        
        with open(os.path.join(path, 'portfolio_optimizer.json'), 'w') as f:
            json.dump(model_data, f)
        
        # Save returns and covariance matrix if available
        if self.returns is not None:
            self.returns.to_csv(os.path.join(path, 'returns.csv'))
        
        if self.cov_matrix is not None:
            self.cov_matrix.to_csv(os.path.join(path, 'covariance_matrix.csv'))
    
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
        model : PortfolioOptimizer
            Loaded model
        """
        # Load model data
        with open(os.path.join(path, 'portfolio_optimizer.json'), 'r') as f:
            model_data = json.load(f)
        
        # Create instance
        instance = cls(model_data['config'])
        instance.assets = model_data['assets']
        
        if model_data['optimal_weights'] is not None:
            instance.optimal_weights = np.array(model_data['optimal_weights'])
        
        instance.optimization_result = model_data['optimization_result']
        
        # Load returns and covariance matrix if available
        if os.path.exists(os.path.join(path, 'returns.csv')):
            instance.returns = pd.read_csv(os.path.join(path, 'returns.csv'), index_col=0)
        
        if os.path.exists(os.path.join(path, 'covariance_matrix.csv')):
            instance.cov_matrix = pd.read_csv(os.path.join(path, 'covariance_matrix.csv'), index_col=0)
        
        return instance

# Example usage
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', periods=252, freq='B')
    
    # Create returns for 5 assets
    returns_data = pd.DataFrame({
        'AAPL': np.random.normal(0.001, 0.02, 252),
        'MSFT': np.random.normal(0.0012, 0.018, 252),
        'AMZN': np.random.normal(0.0015, 0.025, 252),
        'GOOGL': np.random.normal(0.0008, 0.016, 252),
        'BRK.A': np.random.normal(0.0005, 0.012, 252)
    }, index=dates)
    
    # Initialize optimizer
    optimizer = PortfolioOptimizer({
        'optimization_method': 'max_sharpe',
        'risk_free_rate': 0.02,
        'constraints': {
            'min_weight': 0.05,
            'max_weight': 0.4
        }
    })
    
    # Optimize portfolio
    result = optimizer.optimize(returns_data)
    print("Optimization result:")
    print(f"Weights: {result['weights']}")
    print(f"Performance: {result['performance']}")
    
    # Generate efficient frontier
    efficient_frontier = optimizer.generate_efficient_frontier(returns_data, num_portfolios=1000)
    
    # Plot efficient frontier
    fig1 = optimizer.plot_efficient_frontier(efficient_frontier)
    
    # Plot asset allocation
    fig2 = optimizer.plot_asset_allocation()
    
    # Save model
    optimizer.save('portfolio_optimizer')
    
    # Load model
    loaded_optimizer = PortfolioOptimizer.load('portfolio_optimizer')
    
    # Verify loaded model
    print("\nLoaded model config:", loaded_optimizer.config)
    print("Loaded model weights:", loaded_optimizer.optimization_result['weights'])
