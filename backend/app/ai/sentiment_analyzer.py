import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
import joblib
import os
import json

# Download NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class SentimentAnalyzer:
    def __init__(self, config=None):
        """
        Initialize sentiment analysis model for market sentiment prediction
        
        Parameters:
        -----------
        config : dict
            Configuration parameters for the model
        """
        self.config = {
            'model_type': 'logistic_regression',  # Options: 'naive_bayes', 'logistic_regression', 'svm', 'random_forest'
            'max_features': 5000,  # Maximum number of features for vectorizer
            'ngram_range': (1, 2),  # n-gram range for vectorizer
            'use_tfidf': True,  # Whether to use TF-IDF transformation
            'random_state': 42,  # Random seed
            'test_size': 0.2,  # Test size for train-test split
        }
        
        if config:
            self.config.update(config)
        
        self.model = None
        self.pipeline = None
        self.classes = None
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def _preprocess_text(self, text):
        """
        Preprocess text data
        
        Parameters:
        -----------
        text : str
            Input text
            
        Returns:
        --------
        processed_text : str
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        # Join tokens back into text
        processed_text = ' '.join(tokens)
        
        return processed_text
    
    def _build_pipeline(self):
        """
        Build model pipeline
        
        Returns:
        --------
        pipeline : sklearn.pipeline.Pipeline
            Model pipeline
        """
        # Define vectorizer
        vectorizer = CountVectorizer(
            max_features=self.config['max_features'],
            ngram_range=self.config['ngram_range']
        )
        
        # Define steps
        steps = [('vect', vectorizer)]
        
        # Add TF-IDF transformer if specified
        if self.config['use_tfidf']:
            steps.append(('tfidf', TfidfTransformer()))
        
        # Add classifier based on model type
        if self.config['model_type'] == 'naive_bayes':
            steps.append(('clf', MultinomialNB()))
        elif self.config['model_type'] == 'logistic_regression':
            steps.append(('clf', LogisticRegression(random_state=self.config['random_state'])))
        elif self.config['model_type'] == 'svm':
            steps.append(('clf', SVC(probability=True, random_state=self.config['random_state'])))
        elif self.config['model_type'] == 'random_forest':
            steps.append(('clf', RandomForestClassifier(random_state=self.config['random_state'])))
        else:
            raise ValueError(f"Unknown model type: {self.config['model_type']}")
        
        # Create pipeline
        pipeline = Pipeline(steps)
        
        return pipeline
    
    def train(self, data, text_column, label_column, grid_search=False, verbose=1):
        """
        Train sentiment analysis model
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Training data
        text_column : str
            Column name for text data
        label_column : str
            Column name for sentiment labels
        grid_search : bool
            Whether to perform grid search for hyperparameter tuning
        verbose : int
            Verbosity mode
            
        Returns:
        --------
        self : SentimentAnalyzer
            Trained model
        """
        # Preprocess text
        if verbose > 0:
            print("Preprocessing text data...")
        
        data['processed_text'] = data[text_column].apply(self._preprocess_text)
        
        # Get classes
        self.classes = data[label_column].unique()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            data['processed_text'],
            data[label_column],
            test_size=self.config['test_size'],
            random_state=self.config['random_state'],
            stratify=data[label_column]
        )
        
        # Build pipeline
        self.pipeline = self._build_pipeline()
        
        # Train model
        if verbose > 0:
            print(f"Training {self.config['model_type']} model...")
        
        if grid_search:
            # Define parameter grid based on model type
            if self.config['model_type'] == 'naive_bayes':
                param_grid = {
                    'vect__max_features': [3000, 5000, 10000],
                    'vect__ngram_range': [(1, 1), (1, 2), (1, 3)],
                    'clf__alpha': [0.1, 0.5, 1.0]
                }
            elif self.config['model_type'] == 'logistic_regression':
                param_grid = {
                    'vect__max_features': [3000, 5000, 10000],
                    'vect__ngram_range': [(1, 1), (1, 2), (1, 3)],
                    'clf__C': [0.1, 1.0, 10.0]
                }
            elif self.config['model_type'] == 'svm':
                param_grid = {
                    'vect__max_features': [3000, 5000, 10000],
                    'vect__ngram_range': [(1, 1), (1, 2)],
                    'clf__C': [0.1, 1.0, 10.0],
                    'clf__kernel': ['linear', 'rbf']
                }
            elif self.config['model_type'] == 'random_forest':
                param_grid = {
                    'vect__max_features': [3000, 5000, 10000],
                    'vect__ngram_range': [(1, 1), (1, 2)],
                    'clf__n_estimators': [100, 200],
                    'clf__max_depth': [None, 10, 20]
                }
            
            # Create grid search
            grid_search = GridSearchCV(
                self.pipeline,
                param_grid,
                cv=5,
                n_jobs=-1,
                verbose=verbose
            )
            
            # Fit grid search
            grid_search.fit(X_train, y_train)
            
            # Get best model
            self.pipeline = grid_search.best_estimator_
            
            if verbose > 0:
                print(f"Best parameters: {grid_search.best_params_}")
        else:
            # Fit pipeline
            self.pipeline.fit(X_train, y_train)
        
        # Evaluate model
        if verbose > 0:
            print("Evaluating model...")
        
        y_pred = self.pipeline.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
        
        if verbose > 0:
            print(f"Accuracy: {accuracy:.4f}")
            print(f"Precision: {precision:.4f}")
            print(f"Recall: {recall:.4f}")
            print(f"F1 Score: {f1:.4f}")
            print("\nClassification Report:")
            print(classification_report(y_test, y_pred))
        
        self.model = self.pipeline
        
        return self
    
    def predict(self, texts):
        """
        Predict sentiment for new texts
        
        Parameters:
        -----------
        texts : str or list
            Input text(s)
            
        Returns:
        --------
        predictions : dict or list
            Sentiment predictions with probabilities
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        # Handle single text
        single_input = False
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        
        # Preprocess texts
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        # Get predictions and probabilities
        predictions = self.model.predict(processed_texts)
        probabilities = self.model.predict_proba(processed_texts)
        
        # Format results
        results = []
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            result = {
                'text': texts[i],
                'sentiment': pred,
                'confidence': float(max(probs)),
                'probabilities': {cls: float(prob) for cls, prob in zip(self.model.classes_, probs)}
            }
            results.append(result)
        
        # Return single result if input was single text
        if single_input:
            return results[0]
        
        return results
    
    def save(self, path):
        """
        Save model
        
        Parameters:
        -----------
        path : str
            Directory path to save model
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        os.makedirs(path, exist_ok=True)
        
        # Save model
        joblib.dump(self.pipeline, os.path.join(path, 'sentiment_model.pkl'))
        
        # Save config and classes
        with open(os.path.join(path, 'sentiment_config.json'), 'w') as f:
            json.dump({
                'config': self.config,
                'classes': self.classes.tolist() if isinstance(self.classes, np.ndarray) else list(self.classes)
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
        model : SentimentAnalyzer
            Loaded model
        """
        # Load config and classes
        with open(os.path.join(path, 'sentiment_config.json'), 'r') as f:
            data = json.load(f)
        
        # Create instance
        instance = cls(data['config'])
        instance.classes = np.array(data['classes'])
        
        # Load model
        instance.pipeline = joblib.load(os.path.join(path, 'sentiment_model.pkl'))
        instance.model = instance.pipeline
        
        return instance

# Example usage
if __name__ == "__main__":
    # Create sample data
    data = pd.DataFrame({
        'text': [
            "The company reported strong earnings, exceeding analyst expectations.",
            "Revenue growth was impressive, with a 25% increase year-over-year.",
            "The stock price surged after the positive earnings announcement.",
            "Investors are optimistic about the company's future prospects.",
            "The company announced a new product line that could drive growth.",
            "The company missed earnings expectations, disappointing investors.",
            "Revenue declined by 10% compared to the previous quarter.",
            "The stock price plummeted following the negative earnings report.",
            "Analysts downgraded the stock due to concerns about future growth.",
            "The company announced layoffs, signaling potential financial troubles."
        ],
        'sentiment': [
            'positive', 'positive', 'positive', 'positive', 'positive',
            'negative', 'negative', 'negative', 'negative', 'negative'
        ]
    })
    
    # Initialize and train model
    analyzer = SentimentAnalyzer()
    analyzer.train(data, 'text', 'sentiment', verbose=1)
    
    # Make predictions
    new_texts = [
        "The company's revenue exceeded expectations, leading to a stock price increase.",
        "Investors are concerned about the company's declining market share."
    ]
    
    predictions = analyzer.predict(new_texts)
    for pred in predictions:
        print(f"Text: {pred['text']}")
        print(f"Sentiment: {pred['sentiment']}")
        print(f"Confidence: {pred['confidence']:.4f}")
        print()
    
    # Save model
    analyzer.save('sentiment_model')
    
    # Load model
    loaded_analyzer = SentimentAnalyzer.load('sentiment_model')
    
    # Make predictions with loaded model
    loaded_predictions = loaded_analyzer.predict(new_texts)
    for pred in loaded_predictions:
        print(f"Text: {pred['text']}")
        print(f"Sentiment: {pred['sentiment']}")
        print(f"Confidence: {pred['confidence']:.4f}")
        print()
