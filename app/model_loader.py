"""
Model Loader Module
Handles loading and caching of trained ML models and preprocessors
"""

import joblib
import os
from datetime import datetime

class ModelLoader:
    """
    Singleton class to load and cache fraud detection models.
    Ensures models are loaded once and reused across requests.
    """

    _instance = None
    _model = None
    _preprocessor = None
    _model_loaded_at = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.model_path = 'models/best_model.pkl'
        self.preprocessor_path = 'models/preprocessor.pkl'

    def load_model(self, force_reload=False):
        """
        Load the trained fraud detection model.
        Uses cached version if already loaded.

        Args:
            force_reload: Force reload even if model is cached

        Returns:
            Loaded model object
        """
        if self._model is None or force_reload:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(
                    f"Model file not found at {self.model_path}. "
                    "Please run model_training.py first to train the model."
                )

            print(f"Loading model from {self.model_path}...")
            model_data = joblib.load(self.model_path)
            self._model = model_data['model']
            self._model_loaded_at = datetime.now()
            print(f"Model loaded successfully at {self._model_loaded_at}")

        return self._model

    def load_preprocessor(self, force_reload=False):
        """
        Load the data preprocessor pipeline.

        Args:
            force_reload: Force reload even if preprocessor is cached

        Returns:
            Preprocessor object with scaler and encoders
        """
        if self._preprocessor is None or force_reload:
            if not os.path.exists(self.preprocessor_path):
                raise FileNotFoundError(
                    f"Preprocessor not found at {self.preprocessor_path}. "
                    "Please run data_preprocessing.py first."
                )

            print(f"Loading preprocessor from {self.preprocessor_path}...")
            self._preprocessor = joblib.load(self.preprocessor_path)
            print("Preprocessor loaded successfully")

        return self._preprocessor

    def get_model_info(self):
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model metadata
        """
        if self._model is None:
            self.load_model()

        return {
            'model_type': type(self._model).__name__,
            'loaded_at': self._model_loaded_at.isoformat() if self._model_loaded_at else None,
            'model_path': self.model_path,
            'version': '1.0.0'
        }

    def is_model_loaded(self):
        """Check if model is currently loaded in memory"""
        return self._model is not None

    def reload_model(self):
        """Force reload the model from disk"""
        print("Reloading model...")
        self.load_model(force_reload=True)
        self.load_preprocessor(force_reload=True)
        print("Model and preprocessor reloaded")


# Global model loader instance
model_loader = ModelLoader()
