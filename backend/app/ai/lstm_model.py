import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os
import json

class LSTMModel:
    def __init__(self, config=None):
        """
        Initialize LSTM model for financial prediction
        
        Parameters:
        -----------
        config : dict
            Configuration parameters for the model
        """
        self.config = {
            'sequence_length': 60,  # Number of time steps to look back
            'prediction_horizon': 5,  # Number of days to predict ahead
            'features': ['close', 'volume', 'open', 'high', 'low'],  # Features to use
            'target': 'close',  # Target variable to predict
            'lstm_units': 50,  # Number of LSTM units
            'dropout_rate': 0.2,  # Dropout rate
            'dense_units': 25,  # Number of dense units
            'epochs': 50,  # Number of training epochs
            'batch_size': 32,  # Batch size
            'validation_split': 0.2,  # Validation split
            'optimizer': 'adam',  # Optimizer
            'loss': 'mean_squared_error',  # Loss function
            'metrics': ['mae']  # Metrics
        }
        
        if config:
            self.config.update(config)
        
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_scalers = {}
        
    def _prepare_data(self, data):
        """
        Prepare data for LSTM model
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Input data with features
            
        Returns:
        --------
        X : numpy.ndarray
            Input sequences
        y : numpy.ndarray
            Target values
        """
        # Scale features
        scaled_features = {}
        for feature in self.config['features']:
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_features[feature] = scaler.fit_transform(data[feature].values.reshape(-1, 1))
            self.feature_scalers[feature] = scaler
        
        # Scale target
        target_scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_target = target_scaler.fit_transform(data[self.config['target']].values.reshape(-1, 1))
        self.feature_scalers['target'] = target_scaler
        
        # Create sequences
        X, y = [], []
        for i in range(len(data) - self.config['sequence_length'] - self.config['prediction_horizon'] + 1):
            features = []
            for feature in self.config['features']:
                features.append(scaled_features[feature][i:i+self.config['sequence_length']])
            
            X.append(np.hstack(features))
            y.append(scaled_target[i+self.config['sequence_length']+self.config['prediction_horizon']-1])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """
        Build LSTM model
        
        Parameters:
        -----------
        input_shape : tuple
            Shape of input data (sequence_length, num_features)
        """
        model = Sequential()
        model.add(LSTM(units=self.config['lstm_units'], 
                       return_sequences=True, 
                       input_shape=input_shape))
        model.add(Dropout(self.config['dropout_rate']))
        model.add(LSTM(units=self.config['lstm_units'], 
                       return_sequences=False))
        model.add(Dropout(self.config['dropout_rate']))
        model.add(Dense(units=self.config['dense_units'], activation='relu'))
        model.add(Dense(units=1))
        
        model.compile(optimizer=self.config['optimizer'], 
                      loss=self.config['loss'], 
                      metrics=self.config['metrics'])
        
        self.model = model
        return model
    
    def train(self, data, verbose=1):
        """
        Train LSTM model
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Training data
        verbose : int
            Verbosity mode
            
        Returns:
        --------
        history : dict
            Training history
        """
        X, y = self._prepare_data(data)
        
        # Reshape X for LSTM [samples, time steps, features]
        num_features = len(self.config['features'])
        X = X.reshape(X.shape[0], self.config['sequence_length'], num_features)
        
        if self.model is None:
            self.build_model((self.config['sequence_length'], num_features))
        
        history = self.model.fit(
            X, y,
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            validation_split=self.config['validation_split'],
            verbose=verbose
        )
        
        return history.history
    
    def predict(self, data):
        """
        Make predictions with trained model
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Input data for prediction
            
        Returns:
        --------
        predictions : numpy.ndarray
            Predicted values (unscaled)
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        # Prepare data for prediction
        X, _ = self._prepare_data(data)
        
        # Reshape X for LSTM [samples, time steps, features]
        num_features = len(self.config['features'])
        X = X.reshape(X.shape[0], self.config['sequence_length'], num_features)
        
        # Make predictions
        scaled_predictions = self.model.predict(X)
        
        # Inverse transform predictions
        predictions = self.feature_scalers['target'].inverse_transform(scaled_predictions)
        
        return predictions
    
    def evaluate(self, data):
        """
        Evaluate model performance
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Test data
            
        Returns:
        --------
        metrics : dict
            Evaluation metrics
        """
        X, y = self._prepare_data(data)
        
        # Reshape X for LSTM [samples, time steps, features]
        num_features = len(self.config['features'])
        X = X.reshape(X.shape[0], self.config['sequence_length'], num_features)
        
        # Make predictions
        scaled_predictions = self.model.predict(X)
        
        # Inverse transform predictions and actual values
        predictions = self.feature_scalers['target'].inverse_transform(scaled_predictions)
        actual = self.feature_scalers['target'].inverse_transform(y)
        
        # Calculate metrics
        mse = mean_squared_error(actual, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(actual, predictions)
        r2 = r2_score(actual, predictions)
        
        metrics = {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2)
        }
        
        return metrics
    
    def save(self, path):
        """
        Save model and scalers
        
        Parameters:
        -----------
        path : str
            Directory path to save model
        """
        os.makedirs(path, exist_ok=True)
        
        # Save model
        self.model.save(os.path.join(path, 'lstm_model.h5'))
        
        # Save scalers
        for feature, scaler in self.feature_scalers.items():
            joblib.dump(scaler, os.path.join(path, f'scaler_{feature}.pkl'))
        
        # Save config
        with open(os.path.join(path, 'config.json'), 'w') as f:
            json.dump(self.config, f)
    
    @classmethod
    def load(cls, path):
        """
        Load model and scalers
        
        Parameters:
        -----------
        path : str
            Directory path to load model from
            
        Returns:
        --------
        model : LSTMModel
            Loaded model
        """
        # Load config
        with open(os.path.join(path, 'config.json'), 'r') as f:
            config = json.load(f)
        
        # Create instance
        instance = cls(config)
        
        # Load model
        instance.model = tf.keras.models.load_model(os.path.join(path, 'lstm_model.h5'))
        
        # Load scalers
        for feature in instance.config['features'] + ['target']:
            instance.feature_scalers[feature] = joblib.load(os.path.join(path, f'scaler_{feature}.pkl'))
        
        return instance

# Example usage
if __name__ == "__main__":
    # Generate sample data
    dates = pd.date_range(start='2020-01-01', periods=1000, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'close': np.random.normal(100, 10, 1000).cumsum() + 1000,
        'volume': np.random.normal(1000000, 200000, 1000),
        'open': np.random.normal(100, 10, 1000).cumsum() + 1000,
        'high': np.random.normal(100, 10, 1000).cumsum() + 1010,
        'low': np.random.normal(100, 10, 1000).cumsum() + 990
    })
    
    # Split data
    train_data = data.iloc[:800]
    test_data = data.iloc[800-60:]  # Include some overlap for sequence
    
    # Initialize and train model
    model = LSTMModel()
    history = model.train(train_data)
    
    # Evaluate model
    metrics = model.evaluate(test_data)
    print("Evaluation metrics:", metrics)
    
    # Make predictions
    predictions = model.predict(test_data)
    
    # Save model
    model.save('lstm_model')
    
    # Load model
    loaded_model = LSTMModel.load('lstm_model')
    
    # Make predictions with loaded model
    loaded_predictions = loaded_model.predict(test_data)
    
    # Verify predictions are the same
    print("Predictions match:", np.allclose(predictions, loaded_predictions))
