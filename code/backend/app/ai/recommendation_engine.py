import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json
from datetime import datetime, timedelta

class AIRecommendationEngine:
    def __init__(self, config=None):
        """
        Initialize AI recommendation engine
        
        Parameters:
        -----------
        config : dict
            Configuration parameters for the model
        """
        self.config = {
            'model_type': 'ensemble',  # Options: 'random_forest', 'gradient_boosting', 'ensemble'
            'prediction_horizon': 30,  # Days to predict ahead
            'features': [
                'price_momentum', 'volume_trend', 'volatility', 
                'rsi', 'macd', 'sentiment_score', 'market_correlation'
            ],
            'ensemble_weights': {
                'random_forest': 0.5,
                'gradient_boosting': 0.5
            },
            'random_state': 42,  # Random seed
            'n_estimators': 100,  # Number of trees
            'max_depth': 10,  # Maximum depth of trees
            'min_samples_split': 5,  # Minimum samples required to split
            'min_samples_leaf': 2  # Minimum samples required at leaf node
        }
        
        if config:
            self.config.update(config)
        
        self.models = {}
        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()
        self.feature_importance = None
        
    def _preprocess_data(self, data):
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
        # Extract features and target
        X = data[self.config['features']].values
        y = data['target'].values.reshape(-1, 1)
        
        # Scale features and target
        X_scaled = self.feature_scaler.fit_transform(X)
        y_scaled = self.target_scaler.fit_transform(y)
        
        return X_scaled, y_scaled.ravel()
    
    def _create_models(self):
        """
        Create machine learning models
        
        Returns:
        --------
        models : dict
            Dictionary of models
        """
        models = {}
        
        # Random Forest model
        if self.config['model_type'] in ['random_forest', 'ensemble']:
            models['random_forest'] = RandomForestRegressor(
                n_estimators=self.config['n_estimators'],
                max_depth=self.config['max_depth'],
                min_samples_split=self.config['min_samples_split'],
                min_samples_leaf=self.config['min_samples_leaf'],
                random_state=self.config['random_state']
            )
        
        # Gradient Boosting model
        if self.config['model_type'] in ['gradient_boosting', 'ensemble']:
            models['gradient_boosting'] = GradientBoostingRegressor(
                n_estimators=self.config['n_estimators'],
                max_depth=self.config['max_depth'],
                min_samples_split=self.config['min_samples_split'],
                min_samples_leaf=self.config['min_samples_leaf'],
                random_state=self.config['random_state']
            )
        
        return models
    
    def train(self, data):
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
        # Preprocess data
        X, y = self._preprocess_data(data)
        
        # Create models
        self.models = self._create_models()
        
        # Train models
        for name, model in self.models.items():
            model.fit(X, y)
        
        # Calculate feature importance
        self._calculate_feature_importance()
        
        return self
    
    def _calculate_feature_importance(self):
        """
        Calculate feature importance
        
        Returns:
        --------
        feature_importance : dict
            Feature importance for each model
        """
        feature_importance = {}
        
        for name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                feature_importance[name] = {
                    feature: float(imp) for feature, imp in zip(self.config['features'], importance)
                }
        
        self.feature_importance = feature_importance
        return feature_importance
    
    def predict(self, features):
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
        
        # Extract and scale features
        X = features[self.config['features']].values
        X_scaled = self.feature_scaler.transform(X)
        
        # Make predictions with each model
        predictions = {}
        for name, model in self.models.items():
            pred = model.predict(X_scaled)
            predictions[name] = pred
        
        # Combine predictions for ensemble
        if self.config['model_type'] == 'ensemble':
            ensemble_pred = np.zeros_like(predictions[list(predictions.keys())[0]])
            for name, pred in predictions.items():
                weight = self.config['ensemble_weights'].get(name, 1.0 / len(predictions))
                ensemble_pred += pred * weight
            predictions['ensemble'] = ensemble_pred
        
        # Inverse transform predictions
        for name, pred in predictions.items():
            predictions[name] = self.target_scaler.inverse_transform(pred.reshape(-1, 1)).ravel()
        
        # Use the appropriate prediction based on model type
        if self.config['model_type'] == 'ensemble':
            final_predictions = predictions['ensemble']
        else:
            final_predictions = predictions[self.config['model_type']]
        
        # Create recommendations
        recommendations = self._format_recommendations(features, final_predictions)
        
        return recommendations
    
    def _format_recommendations(self, features, predictions):
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
        # Get asset symbols
        if 'symbol' in features.columns:
            symbols = features['symbol'].tolist()
        else:
            symbols = [f"Asset_{i+1}" for i in range(len(predictions))]
        
        # Create recommendation items
        items = []
        for i, (symbol, prediction) in enumerate(zip(symbols, predictions)):
            # Determine recommendation type based on prediction
            if prediction > 0.05:
                rec_type = "buy"
            elif prediction < -0.05:
                rec_type = "sell"
            else:
                rec_type = "hold"
            
            # Calculate confidence based on prediction magnitude
            confidence = min(abs(prediction) * 10, 1.0) * 100
            
            # Create recommendation item
            item = {
                "symbol": symbol,
                "recommendation": rec_type,
                "predicted_return": float(prediction),
                "confidence": float(confidence),
                "time_horizon": f"{self.config['prediction_horizon']} days",
                "timestamp": datetime.now().isoformat()
            }
            
            # Add feature values if available
            if all(f in features.columns for f in self.config['features']):
                item["features"] = {
                    feature: float(features[feature].iloc[i]) 
                    for feature in self.config['features']
                }
            
            items.append(item)
        
        # Sort recommendations by absolute predicted return
        items.sort(key=lambda x: abs(x["predicted_return"]), reverse=True)
        
        # Create recommendations dictionary
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "prediction_horizon": self.config['prediction_horizon'],
            "model_type": self.config['model_type'],
            "recommendations": items,
            "market_outlook": self._generate_market_outlook(predictions)
        }
        
        return recommendations
    
    def _generate_market_outlook(self, predictions):
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
        # Calculate average prediction
        avg_prediction = np.mean(predictions)
        
        # Determine market outlook
        if avg_prediction > 0.03:
            outlook = "bullish"
        elif avg_prediction < -0.03:
            outlook = "bearish"
        else:
            outlook = "neutral"
        
        # Calculate confidence based on prediction magnitude and consistency
        confidence = min(abs(avg_prediction) * 15, 1.0) * 100
        
        # Generate forecast dates
        today = datetime.now()
        forecast_dates = [
            (today + timedelta(days=7)).strftime("%Y-%m-%d"),
            (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            (today + timedelta(days=30)).strftime("%Y-%m-%d")
        ]
        
        # Create market outlook dictionary
        market_outlook = {
            "overall_outlook": outlook,
            "confidence": float(confidence),
            "average_predicted_return": float(avg_prediction),
            "volatility_expectation": "high" if np.std(predictions) > 0.05 else "moderate",
            "forecast_period": {
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=self.config['prediction_horizon'])).strftime("%Y-%m-%d")
            },
            "key_indicators": {
                "positive_recommendations": int(np.sum(predictions > 0.05)),
                "negative_recommendations": int(np.sum(predictions < -0.05)),
                "neutral_recommendations": int(np.sum((predictions >= -0.05) & (predictions <= 0.05)))
            },
            "forecast_trend": [
                {"date": forecast_dates[0], "outlook": outlook, "confidence": float(confidence * 0.9)},
                {"date": forecast_dates[1], "outlook": outlook, "confidence": float(confidence * 0.8)},
                {"date": forecast_dates[2], "outlook": outlook, "confidence": float(confidence * 0.7)}
            ]
        }
        
        return market_outlook
    
    def get_feature_importance(self):
        """
        Get feature importance
        
        Returns:
        --------
        importance : dict
            Feature importance information
        """
        if self.feature_importance is None:
            raise ValueError("Feature importance not calculated yet. Train models first.")
        
        # Calculate average importance for ensemble
        if len(self.feature_importance) > 1:
            avg_importance = {}
            for feature in self.config['features']:
                avg_importance[feature] = np.mean([
                    imp[feature] for imp in self.feature_importance.values()
                ])
            self.feature_importance['ensemble'] = avg_importance
        
        # Use the appropriate importance based on model type
        if self.config['model_type'] == 'ensemble':
            importance = self.feature_importance['ensemble']
        else:
            importance = self.feature_importance[self.config['model_type']]
        
        # Sort features by importance
        sorted_importance = {
            k: v for k, v in sorted(importance.items(), key=lambda item: item[1], reverse=True)
        }
        
        return sorted_importance
    
    def save(self, path):
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
        
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, os.path.join(path, f"recommendation_{name}_model.pkl"))
        
        # Save scalers
        joblib.dump(self.feature_scaler, os.path.join(path, "recommendation_feature_scaler.pkl"))
        joblib.dump(self.target_scaler, os.path.join(path, "recommendation_target_scaler.pkl"))
        
        # Save config and feature importance
        model_data = {
            'config': self.config,
            'feature_importance': self.feature_importance
        }
        
        with open(os.path.join(path, "recommendation_data.json"), 'w') as f:
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
        model : AIRecommendationEngine
            Loaded model
        """
        # Load model data
        with open(os.path.join(path, "recommendation_data.json"), 'r') as f:
            model_data = json.load(f)
        
        # Create instance
        instance = cls(model_data['config'])
        instance.feature_importance = model_data['feature_importance']
        
        # Load models
        instance.models = {}
        if instance.config['model_type'] in ['random_forest', 'ensemble']:
            instance.models['random_forest'] = joblib.load(
                os.path.join(path, "recommendation_random_forest_model.pkl")
            )
        
        if instance.config['model_type'] in ['gradient_boosting', 'ensemble']:
            instance.models['gradient_boosting'] = joblib.load(
                os.path.join(path, "recommendation_gradient_boosting_model.pkl")
            )
        
        # Load scalers
        instance.feature_scaler = joblib.load(os.path.join(path, "recommendation_feature_scaler.pkl"))
        instance.target_scaler = joblib.load(os.path.join(path, "recommendation_target_scaler.pkl"))
        
        return instance

# Example usage
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    n_assets = 50
    
    # Create features
    features = []
    targets = []
    
    for i in range(n_assets):
        # Generate random features
        price_momentum = np.random.normal(0.01, 0.05, n_samples)
        volume_trend = np.random.normal(0.02, 0.1, n_samples)
        volatility = np.random.uniform(0.1, 0.5, n_samples)
        rsi = np.random.uniform(30, 70, n_samples)
        macd = np.random.normal(0, 0.1, n_samples)
        sentiment_score = np.random.normal(0.5, 0.2, n_samples)
        market_correlation = np.random.uniform(-0.5, 0.9, n_samples)
        
        # Generate target (simulated future return)
        # Target is influenced by features with some noise
        target = (
            0.3 * price_momentum +
            0.1 * volume_trend -
            0.2 * volatility +
            0.002 * (rsi - 50) +
            0.5 * macd +
            0.2 * sentiment_score +
            0.1 * market_correlation +
            np.random.normal(0, 0.02, n_samples)  # Noise
        )
        
        # Create asset data
        for j in range(n_samples):
            features.append({
                'symbol': f"ASSET_{i+1}",
                'price_momentum': price_momentum[j],
                'volume_trend': volume_trend[j],
                'volatility': volatility[j],
                'rsi': rsi[j],
                'macd': macd[j],
                'sentiment_score': sentiment_score[j],
                'market_correlation': market_correlation[j],
                'target': target[j]
            })
    
    # Convert to DataFrame
    data = pd.DataFrame(features)
    
    # Split data for training
    train_data = data.sample(frac=0.8, random_state=42)
    test_data = data.drop(train_data.index)
    
    # Initialize and train recommendation engine
    engine = AIRecommendationEngine()
    engine.train(train_data)
    
    # Get feature importance
    importance = engine.get_feature_importance()
    print("Feature Importance:")
    for feature, imp in importance.items():
        print(f"{feature}: {imp:.4f}")
    
    # Generate recommendations for test data
    test_features = test_data.drop('target', axis=1)
    recommendations = engine.predict(test_features)
    
    print("\nRecommendations:")
    for i, rec in enumerate(recommendations['recommendations'][:5]):  # Show top 5
        print(f"{i+1}. {rec['symbol']}: {rec['recommendation']} (Predicted Return: {rec['predicted_return']:.2%}, Confidence: {rec['confidence']:.1f}%)")
    
    print("\nMarket Outlook:")
    print(f"Overall: {recommendations['market_outlook']['overall_outlook']}")
    print(f"Confidence: {recommendations['market_outlook']['confidence']:.1f}%")
    print(f"Average Predicted Return: {recommendations['market_outlook']['average_predicted_return']:.2%}")
    
    # Save model
    engine.save('recommendation_engine')
    
    # Load model
    loaded_engine = AIRecommendationEngine.load('recommendation_engine')
    
    # Verify loaded model
    loaded_recommendations = loaded_engine.predict(test_features)
    print("\nLoaded Model Recommendations (first item):")
    print(loaded_recommendations['recommendations'][0])
