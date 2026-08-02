import json
import logging
import os
import re
from typing import Any

import joblib
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)


class SentimentAnalyzer:

    def __init__(self, config: Any = None) -> None:
        """
        Initialize sentiment analysis model for market sentiment prediction

        Parameters:
        -----------
        config : dict
            Configuration parameters for the model
        """
        self.config = {
            "model_type": "logistic_regression",
            "max_features": 5000,
            "ngram_range": (1, 2),
            "use_tfidf": True,
            "random_state": 42,
            "test_size": 0.2,
        }
        if config:
            self.config.update(config)
        self.model = None
        self.pipeline = None
        self.classes = None
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english"))

    def _preprocess_text(self, text: Any) -> Any:
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
        text = text.lower()
        text = re.sub("http\\S+", "", text)
        text = re.sub("[^a-zA-Z\\s]", "", text)
        tokens = word_tokenize(text)
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]
        processed_text = " ".join(tokens)
        return processed_text

    def _build_pipeline(self) -> Any:
        """
        Build model pipeline

        Returns:
        --------
        pipeline : sklearn.pipeline.Pipeline
            Model pipeline
        """
        vectorizer = CountVectorizer(
            max_features=self.config["max_features"],
            ngram_range=self.config["ngram_range"],
        )
        steps = [("vect", vectorizer)]
        if self.config["use_tfidf"]:
            steps.append(("tfidf", TfidfTransformer()))
        if self.config["model_type"] == "naive_bayes":
            steps.append(("clf", MultinomialNB()))
        elif self.config["model_type"] == "logistic_regression":
            steps.append(
                ("clf", LogisticRegression(random_state=self.config["random_state"]))
            )
        elif self.config["model_type"] == "svm":
            steps.append(
                ("clf", SVC(probability=True, random_state=self.config["random_state"]))
            )
        elif self.config["model_type"] == "random_forest":
            steps.append(
                (
                    "clf",
                    RandomForestClassifier(random_state=self.config["random_state"]),
                )
            )
        else:
            raise ValueError(f"Unknown model type: {self.config['model_type']}")
        pipeline = Pipeline(steps)
        return pipeline

    def train(
        self,
        data: Any,
        text_column: Any,
        label_column: Any,
        grid_search: Any = False,
        verbose: Any = 1,
    ) -> Any:
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
        if verbose > 0:
            logger.info("Preprocessing data...")
        data["processed_text"] = data[text_column].apply(self._preprocess_text)
        self.classes = data[label_column].unique()
        X_train, X_test, y_train, y_test = train_test_split(
            data["processed_text"],
            data[label_column],
            test_size=self.config["test_size"],
            random_state=self.config["random_state"],
            stratify=data[label_column],
        )
        self.pipeline = self._build_pipeline()
        if verbose > 0:
            logger.info("Training model...")
        if grid_search:
            if self.config["model_type"] == "naive_bayes":
                param_grid = {
                    "vect__max_features": [3000, 5000, 10000],
                    "vect__ngram_range": [(1, 1), (1, 2), (1, 3)],
                    "clf__alpha": [0.1, 0.5, 1.0],
                }
            elif self.config["model_type"] == "logistic_regression":
                param_grid = {
                    "vect__max_features": [3000, 5000, 10000],
                    "vect__ngram_range": [(1, 1), (1, 2), (1, 3)],
                    "clf__C": [0.1, 1.0, 10.0],
                }
            elif self.config["model_type"] == "svm":
                param_grid = {
                    "vect__max_features": [3000, 5000, 10000],
                    "vect__ngram_range": [(1, 1), (1, 2)],
                    "clf__C": [0.1, 1.0, 10.0],
                    "clf__kernel": ["linear", "rbf"],
                }
            elif self.config["model_type"] == "random_forest":
                param_grid = {
                    "vect__max_features": [3000, 5000, 10000],
                    "vect__ngram_range": [(1, 1), (1, 2)],
                    "clf__n_estimators": [100, 200],
                    "clf__max_depth": [None, 10, 20],
                }
            grid_search = GridSearchCV(
                self.pipeline, param_grid, cv=5, n_jobs=-1, verbose=verbose
            )
            grid_search.fit(X_train, y_train)
            self.pipeline = grid_search.best_estimator_
            if verbose > 0:
                logger.info(f"Best parameters: {grid_search.best_params_}")
            else:
                self.pipeline.fit(X_train, y_train)
        if verbose > 0:
            logger.info("Evaluating model...")
        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average="weighted"
        )
        if verbose > 0:
            logger.info(
                f"Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}"
            )
        self.model = self.pipeline
        return self

    def predict(self, texts: Any) -> Any:
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
        single_input = False
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        processed_texts = [self._preprocess_text(text) for text in texts]
        predictions = self.model.predict(processed_texts)
        probabilities = self.model.predict_proba(processed_texts)
        results = []
        for i, (pred, probs) in enumerate(
            zip(predictions, probabilities, strict=False)
        ):
            result = {
                "text": texts[i],
                "sentiment": pred,
                "confidence": float(max(probs)),
                "probabilities": {
                    cls: float(prob)
                    for cls, prob in zip(self.model.classes_, probs, strict=False)
                },
            }
            results.append(result)
        if single_input:
            return results[0]
        return results

    def save(self, path: Any) -> Any:
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
        joblib.dump(self.pipeline, os.path.join(path, "sentiment_model.pkl"))
        with open(os.path.join(path, "sentiment_config.json"), "w") as f:
            json.dump(
                {
                    "config": self.config,
                    "classes": (
                        self.classes.tolist()
                        if isinstance(self.classes, np.ndarray)
                        else list(self.classes)
                    ),
                },
                f,
            )

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
        model : SentimentAnalyzer
            Loaded model
        """
        with open(os.path.join(path, "sentiment_config.json"), "r") as f:
            data = json.load(f)
        instance = cls(data["config"])
        instance.classes = np.array(data["classes"])
        instance.pipeline = joblib.load(os.path.join(path, "sentiment_model.pkl"))
        instance.model = instance.pipeline
        return instance


if __name__ == "__main__":
    data = pd.DataFrame(
        {
            "text": [
                "The company reported strong earnings, exceeding analyst expectations.",
                "Revenue growth was impressive, with a 25% increase year-over-year.",
                "The stock price surged after the positive earnings announcement.",
                "Investors are optimistic about the company's future prospects.",
                "The company announced a new product line that could drive growth.",
                "The company missed earnings expectations, disappointing investors.",
                "Revenue declined by 10% compared to the previous quarter.",
                "The stock price plummeted following the negative earnings report.",
                "Analysts downgraded the stock due to concerns about future growth.",
                "The company announced layoffs, signaling potential financial troubles.",
            ],
            "sentiment": [
                "positive",
                "positive",
                "positive",
                "positive",
                "positive",
                "negative",
                "negative",
                "negative",
                "negative",
                "negative",
            ],
        }
    )
    analyzer = SentimentAnalyzer()
    analyzer.train(data, "text", "sentiment", verbose=1)
    new_texts = [
        "The company's revenue exceeded expectations, leading to a stock price increase.",
        "Investors are concerned about the company's declining market share.",
    ]
    predictions = analyzer.predict(new_texts)
    for pred in predictions:
        logger.info(
            f"Text: {pred['text']}, Sentiment: {pred['sentiment']}, Confidence: {pred['confidence']:.2f}"
        )
    analyzer.save("sentiment_model")
    loaded_analyzer = SentimentAnalyzer.load("sentiment_model")
    loaded_predictions = loaded_analyzer.predict(new_texts)
    for pred in loaded_predictions:
        logger.info(
            f"Text: {pred['text']}, Sentiment: {pred['sentiment']}, Confidence: {pred['confidence']:.2f}"
        )
