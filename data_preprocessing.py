"""
Data Preprocessing Module for Fraud Detection
Handles data splitting, scaling, class imbalance, and preparation for model training
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTETomek
import joblib
import warnings
warnings.filterwarnings('ignore')

class FraudDataPreprocessor:
    """
    Prepares fraud detection data for model training.
    Handles scaling, encoding, class imbalance, and train/test splitting.
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        self.target_column = 'Is Fraud?'

    def identify_feature_types(self, df):
        """
        Categorize features into numeric, categorical, and target.
        """
        print("Identifying feature types...")

        # Features to exclude from model training
        exclude_features = [
            'User', 'Card', 'DateTime', 'Year', 'Month', 'Day', 'Time',
            'Merchant Name', 'Is Fraud?', 'Person', 'CARD INDEX',
            'Errors?', 'Card Number', 'Merchant City', 'Zip'
        ]

        # Get all column names
        all_columns = df.columns.tolist()

        # Numeric features
        numeric_features = df.select_dtypes(include=['int64', 'float64', 'int32']).columns.tolist()
        numeric_features = [f for f in numeric_features if f not in exclude_features]

        # Categorical features
        categorical_features = df.select_dtypes(include=['object', 'category']).columns.tolist()
        categorical_features = [f for f in categorical_features if f not in exclude_features]

        print(f"Found {len(numeric_features)} numeric features")
        print(f"Found {len(categorical_features)} categorical features")

        return numeric_features, categorical_features

    def encode_categorical_features(self, df, categorical_features, is_training=True):
        """
        Encode categorical variables using label encoding or one-hot encoding.
        """
        print("Encoding categorical features...")

        df_encoded = df.copy()

        for feature in categorical_features:
            if feature not in df_encoded.columns:
                continue

            if is_training:
                # Fit and transform for training data
                le = LabelEncoder()
                df_encoded[feature] = le.fit_transform(df_encoded[feature].astype(str))
                self.label_encoders[feature] = le
            else:
                # Transform using existing encoder for test data
                if feature in self.label_encoders:
                    le = self.label_encoders[feature]
                    # Handle unseen categories
                    df_encoded[feature] = df_encoded[feature].astype(str).apply(
                        lambda x: x if x in le.classes_ else 'unknown'
                    )
                    # Add unknown category if needed
                    if 'unknown' not in le.classes_:
                        le.classes_ = np.append(le.classes_, 'unknown')
                    df_encoded[feature] = le.transform(df_encoded[feature])

        print(f"Encoded {len(categorical_features)} categorical features")
        return df_encoded

    def handle_missing_values(self, df, numeric_features, categorical_features):
        """
        Fill missing values appropriately for numeric and categorical features.
        """
        print("Handling missing values...")

        df_filled = df.copy()

        # Fill numeric missing values with median
        for feature in numeric_features:
            if feature in df_filled.columns:
                median_value = df_filled[feature].median()
                df_filled[feature] = df_filled[feature].fillna(median_value)

        # Fill categorical missing values with mode
        for feature in categorical_features:
            if feature in df_filled.columns:
                mode_value = df_filled[feature].mode()[0] if len(df_filled[feature].mode()) > 0 else 'unknown'
                df_filled[feature] = df_filled[feature].fillna(mode_value)

        print("Missing values handled")
        return df_filled

    def scale_features(self, X_train, X_test=None):
        """
        Scale numeric features using StandardScaler.
        """
        print("Scaling features...")

        # Fit and transform training data
        X_train_scaled = self.scaler.fit_transform(X_train)

        if X_test is not None:
            # Transform test data
            X_test_scaled = self.scaler.transform(X_test)
            print("Scaled training and test data")
            return X_train_scaled, X_test_scaled
        else:
            print("Scaled training data")
            return X_train_scaled

    def split_data(self, df, test_size=0.2, random_state=42, stratify=True):
        """
        Split data into train and test sets with optional stratification.
        Stratification is crucial for imbalanced datasets.
        """
        print("\n" + "=" * 80)
        print("SPLITTING DATA")
        print("=" * 80)

        # Separate features and target
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]

        print(f"\nTotal samples: {len(df)}")
        print(f"Fraud cases: {y.sum()} ({y.mean()*100:.2f}%)")
        print(f"Legitimate cases: {len(y) - y.sum()} ({(1-y.mean())*100:.2f}%)")

        # Stratified split to maintain fraud ratio
        stratify_param = y if stratify else None

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_param
        )

        print(f"\nTraining set: {len(X_train)} samples")
        print(f"  - Fraud: {y_train.sum()} ({y_train.mean()*100:.2f}%)")
        print(f"  - Legitimate: {len(y_train) - y_train.sum()} ({(1-y_train.mean())*100:.2f}%)")

        print(f"\nTest set: {len(X_test)} samples")
        print(f"  - Fraud: {y_test.sum()} ({y_test.mean()*100:.2f}%)")
        print(f"  - Legitimate: {len(y_test) - y_test.sum()} ({(1-y_test.mean())*100:.2f}%)")

        return X_train, X_test, y_train, y_test

    def handle_class_imbalance(self, X_train, y_train, method='smote', sampling_strategy='auto'):
        """
        Handle class imbalance using various resampling techniques.

        Methods:
            - 'smote': Synthetic Minority Over-sampling Technique
            - 'undersample': Random undersampling of majority class
            - 'smotetomek': SMOTE followed by Tomek links cleaning
            - 'none': No resampling
        """
        print("\n" + "=" * 80)
        print(f"HANDLING CLASS IMBALANCE - Method: {method.upper()}")
        print("=" * 80)

        print(f"\nOriginal distribution:")
        print(f"  - Samples: {len(y_train)}")
        print(f"  - Fraud: {y_train.sum()} ({y_train.mean()*100:.2f}%)")
        print(f"  - Legitimate: {len(y_train) - y_train.sum()} ({(1-y_train.mean())*100:.2f}%)")

        if method == 'none':
            print("\nNo resampling applied")
            return X_train, y_train

        if method == 'smote':
            sampler = SMOTE(sampling_strategy=sampling_strategy, random_state=42)
        elif method == 'undersample':
            sampler = RandomUnderSampler(sampling_strategy=sampling_strategy, random_state=42)
        elif method == 'smotetomek':
            sampler = SMOTETomek(sampling_strategy=sampling_strategy, random_state=42)
        else:
            raise ValueError(f"Unknown resampling method: {method}")

        X_resampled, y_resampled = sampler.fit_resample(X_train, y_train)

        print(f"\nResampled distribution:")
        print(f"  - Samples: {len(y_resampled)}")
        print(f"  - Fraud: {y_resampled.sum()} ({y_resampled.mean()*100:.2f}%)")
        print(f"  - Legitimate: {len(y_resampled) - y_resampled.sum()} ({(1-y_resampled.mean())*100:.2f}%)")

        return X_resampled, y_resampled

    def prepare_data_for_training(self, df, test_size=0.2, balance_method='smote',
                                  sampling_strategy='auto', scale=True):
        """
        Complete preprocessing pipeline from raw data to model-ready arrays.

        Args:
            df: DataFrame with engineered features
            test_size: Proportion of data for testing
            balance_method: Method to handle class imbalance
            sampling_strategy: Ratio for resampling (auto, float, or dict)
            scale: Whether to scale features

        Returns:
            X_train, X_test, y_train, y_test: Processed train and test sets
        """
        print("\n" + "=" * 80)
        print("DATA PREPROCESSING PIPELINE")
        print("=" * 80)

        # Identify feature types
        numeric_features, categorical_features = self.identify_feature_types(df)

        # Handle missing values
        df_clean = self.handle_missing_values(df, numeric_features, categorical_features)

        # Encode categorical features
        df_encoded = self.encode_categorical_features(df_clean, categorical_features, is_training=True)

        # Store feature columns for later use
        feature_columns = numeric_features + categorical_features
        feature_columns = [f for f in feature_columns if f in df_encoded.columns]
        self.feature_columns = feature_columns

        print(f"\nFinal feature set: {len(self.feature_columns)} features")

        # Split data
        X_train, X_test, y_train, y_test = self.split_data(
            df_encoded[self.feature_columns + [self.target_column]],
            test_size=test_size,
            stratify=True
        )

        # Handle class imbalance on training data only
        X_train_balanced, y_train_balanced = self.handle_class_imbalance(
            X_train, y_train,
            method=balance_method,
            sampling_strategy=sampling_strategy
        )

        # Scale features if requested
        if scale:
            X_train_scaled, X_test_scaled = self.scale_features(
                X_train_balanced, X_test
            )
            print("\nData preprocessing complete!")
            return X_train_scaled, X_test_scaled, y_train_balanced, y_test
        else:
            print("\nData preprocessing complete!")
            return X_train_balanced, X_test, y_train_balanced, y_test

    def save_preprocessor(self, filepath='models/preprocessor.pkl'):
        """
        Save the preprocessor for later use in production.
        """
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        preprocessor_data = {
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns
        }
        joblib.dump(preprocessor_data, filepath)
        print(f"Preprocessor saved to: {filepath}")

    def load_preprocessor(self, filepath='models/preprocessor.pkl'):
        """
        Load a saved preprocessor.
        """
        preprocessor_data = joblib.load(filepath)
        self.scaler = preprocessor_data['scaler']
        self.label_encoders = preprocessor_data['label_encoders']
        self.feature_columns = preprocessor_data['feature_columns']
        print(f"Preprocessor loaded from: {filepath}")


if __name__ == "__main__":
    print("Loading engineered features...")

    # Load data with features
    try:
        df = pd.read_csv('detection_data/transactions_with_features.csv')
        print(f"Loaded {len(df)} transactions with {len(df.columns)} columns")
    except FileNotFoundError:
        print("Error: Please run feature_engineering.py first to generate features")
        exit(1)

    # Initialize preprocessor
    preprocessor = FraudDataPreprocessor()

    # Prepare data with different imbalance handling methods
    print("\n\n" + "=" * 80)
    print("TESTING DIFFERENT RESAMPLING METHODS")
    print("=" * 80)

    methods = ['none', 'smote', 'undersample']

    for method in methods:
        print(f"\n\nTesting method: {method.upper()}")
        print("-" * 80)

        X_train, X_test, y_train, y_test = preprocessor.prepare_data_for_training(
            df,
            test_size=0.2,
            balance_method=method,
            sampling_strategy='auto' if method != 'none' else None,
            scale=True
        )

        print(f"\nFinal shapes:")
        print(f"  X_train: {X_train.shape}")
        print(f"  X_test: {X_test.shape}")
        print(f"  y_train: {y_train.shape}")
        print(f"  y_test: {y_test.shape}")

    # Save preprocessor for later use
    print("\n\nSaving preprocessor...")
    preprocessor.save_preprocessor('models/preprocessor.pkl')

    print("\n" + "=" * 80)
    print("PREPROCESSING COMPLETE")
    print("=" * 80)
    print("\nData is ready for model training!")
