"""
Fraud Detection Model Training Module
Trains and evaluates machine learning models for fraud detection
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve, f1_score,
    precision_score, recall_score, accuracy_score
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import joblib
import warnings
warnings.filterwarnings('ignore')

class FraudModelTrainer:
    """
    Trains various machine learning models for fraud detection.
    Evaluates performance using appropriate metrics for imbalanced data.
    """

    def __init__(self):
        self.models = {}
        self.model_results = {}
        self.best_model = None
        self.best_model_name = None

    def train_logistic_regression(self, X_train, y_train, class_weight='balanced'):
        """
        Train logistic regression baseline model.
        Simple but effective starting point.
        """
        print("\nTraining Logistic Regression...")

        model = LogisticRegression(
            class_weight=class_weight,
            max_iter=1000,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)
        self.models['logistic_regression'] = model

        print("Logistic Regression training complete")
        return model

    def train_random_forest(self, X_train, y_train, class_weight='balanced'):
        """
        Train Random Forest classifier.
        Good for capturing non-linear patterns and feature importance.
        """
        print("\nTraining Random Forest...")

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight=class_weight,
            random_state=42,
            n_jobs=-1,
            verbose=0
        )

        model.fit(X_train, y_train)
        self.models['random_forest'] = model

        print("Random Forest training complete")
        return model

    def train_xgboost(self, X_train, y_train):
        """
        Train XGBoost classifier.
        State-of-the-art gradient boosting for fraud detection.
        """
        print("\nTraining XGBoost...")

        # Calculate scale_pos_weight for imbalanced data
        scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

        model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss'
        )

        model.fit(X_train, y_train)
        self.models['xgboost'] = model

        print("XGBoost training complete")
        return model

    def train_lightgbm(self, X_train, y_train):
        """
        Train LightGBM classifier.
        Fast and efficient gradient boosting.
        """
        print("\nTraining LightGBM...")

        # Calculate scale_pos_weight
        scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

        model = LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )

        model.fit(X_train, y_train)
        self.models['lightgbm'] = model

        print("LightGBM training complete")
        return model

    def evaluate_model(self, model, model_name, X_test, y_test):
        """
        Comprehensive model evaluation with fraud-specific metrics.
        """
        print(f"\n{'=' * 80}")
        print(f"EVALUATING {model_name.upper()}")
        print(f"{'=' * 80}")

        # Make predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc_roc = roc_auc_score(y_test, y_pred_proba)

        # Store results
        self.model_results[model_name] = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc_roc': auc_roc,
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }

        # Print metrics
        print(f"\nPerformance Metrics:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
        print(f"  AUC-ROC:   {auc_roc:.4f}")

        # Confusion Matrix
        print(f"\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        print(f"\n  True Negatives:  {cm[0, 0]}")
        print(f"  False Positives: {cm[0, 1]}")
        print(f"  False Negatives: {cm[1, 0]}")
        print(f"  True Positives:  {cm[1, 1]}")

        # Classification Report
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud']))

        return self.model_results[model_name]

    def train_all_models(self, X_train, y_train):
        """
        Train all baseline models.
        """
        print("\n" + "=" * 80)
        print("TRAINING ALL BASELINE MODELS")
        print("=" * 80)

        models_trained = []

        # Train Logistic Regression
        try:
            self.train_logistic_regression(X_train, y_train)
            models_trained.append('logistic_regression')
        except Exception as e:
            print(f"Error training Logistic Regression: {e}")

        # Train Random Forest
        try:
            self.train_random_forest(X_train, y_train)
            models_trained.append('random_forest')
        except Exception as e:
            print(f"Error training Random Forest: {e}")

        # Train XGBoost
        try:
            self.train_xgboost(X_train, y_train)
            models_trained.append('xgboost')
        except Exception as e:
            print(f"Error training XGBoost: {e}")

        # Train LightGBM
        try:
            self.train_lightgbm(X_train, y_train)
            models_trained.append('lightgbm')
        except Exception as e:
            print(f"Error training LightGBM: {e}")

        print(f"\n{len(models_trained)} models trained successfully")
        return models_trained

    def evaluate_all_models(self, X_test, y_test):
        """
        Evaluate all trained models.
        """
        print("\n" + "=" * 80)
        print("EVALUATING ALL MODELS")
        print("=" * 80)

        for model_name, model in self.models.items():
            self.evaluate_model(model, model_name, X_test, y_test)

        # Find best model based on F1 score (good balance for fraud detection)
        best_f1 = 0
        for model_name, results in self.model_results.items():
            if results['f1_score'] > best_f1:
                best_f1 = results['f1_score']
                self.best_model_name = model_name
                self.best_model = self.models[model_name]

        print(f"\n" + "=" * 80)
        print(f"BEST MODEL: {self.best_model_name.upper()}")
        print(f"F1-Score: {best_f1:.4f}")
        print(f"=" * 80)

    def compare_models(self, save_path='plots/model_comparison.png'):
        """
        Create visual comparison of all models.
        """
        print("\nCreating model comparison plots...")

        if not self.model_results:
            print("No model results to compare")
            return

        # Extract metrics for plotting
        models = list(self.model_results.keys())
        metrics = ['precision', 'recall', 'f1_score', 'auc_roc']

        # Create comparison dataframe
        comparison_data = []
        for model_name in models:
            for metric in metrics:
                comparison_data.append({
                    'Model': model_name.replace('_', ' ').title(),
                    'Metric': metric.replace('_', ' ').title(),
                    'Value': self.model_results[model_name][metric]
                })

        df_comparison = pd.DataFrame(comparison_data)

        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Model Performance Comparison', fontsize=16, fontweight='bold')

        for idx, metric in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]
            metric_data = df_comparison[df_comparison['Metric'] == metric.replace('_', ' ').title()]

            bars = ax.bar(metric_data['Model'], metric_data['Value'])

            # Color bars
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
            for bar, color in zip(bars, colors):
                bar.set_color(color)

            ax.set_ylabel('Score')
            ax.set_title(metric.replace('_', ' ').title())
            ax.set_ylim(0, 1)
            ax.grid(axis='y', alpha=0.3)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Model comparison plot saved to: {save_path}")

    def plot_roc_curves(self, X_test, y_test, save_path='plots/roc_curves.png'):
        """
        Plot ROC curves for all models.
        """
        print("\nCreating ROC curves...")

        plt.figure(figsize=(10, 8))

        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']

        for idx, (model_name, model) in enumerate(self.models.items()):
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
            auc = roc_auc_score(y_test, y_pred_proba)

            plt.plot(fpr, tpr, label=f'{model_name.replace("_", " ").title()} (AUC = {auc:.3f})',
                    linewidth=2, color=colors[idx % len(colors)])

        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier', linewidth=1)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curves - Model Comparison', fontsize=14, fontweight='bold')
        plt.legend(loc='lower right', fontsize=10)
        plt.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"ROC curves saved to: {save_path}")

    def plot_confusion_matrices(self, X_test, y_test, save_path='plots/confusion_matrices.png'):
        """
        Plot confusion matrices for all models.
        """
        print("\nCreating confusion matrices...")

        n_models = len(self.models)
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.ravel()

        for idx, (model_name, model) in enumerate(self.models.items()):
            y_pred = model.predict(X_test)
            cm = confusion_matrix(y_test, y_pred)

            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                       cbar=True, square=True)
            axes[idx].set_title(f'{model_name.replace("_", " ").title()}', fontweight='bold')
            axes[idx].set_ylabel('Actual')
            axes[idx].set_xlabel('Predicted')
            axes[idx].set_xticklabels(['Legitimate', 'Fraud'])
            axes[idx].set_yticklabels(['Legitimate', 'Fraud'])

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Confusion matrices saved to: {save_path}")

    def save_best_model(self, filepath='models/best_model.pkl'):
        """
        Save the best performing model.
        """
        if self.best_model is None:
            print("No best model identified yet. Run evaluate_all_models first.")
            return

        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        model_data = {
            'model': self.best_model,
            'model_name': self.best_model_name,
            'metrics': self.model_results[self.best_model_name]
        }

        joblib.dump(model_data, filepath)
        print(f"\nBest model ({self.best_model_name}) saved to: {filepath}")

    def save_all_models(self, directory='models'):
        """
        Save all trained models.
        """
        import os
        os.makedirs(directory, exist_ok=True)

        for model_name, model in self.models.items():
            filepath = f"{directory}/{model_name}.pkl"
            joblib.dump(model, filepath)
            print(f"Saved {model_name} to: {filepath}")


if __name__ == "__main__":
    print("Loading preprocessed data...")

    # Load data
    from data_preprocessing import FraudDataPreprocessor

    df = pd.read_csv('detection_data/transactions_with_features.csv')
    print(f"Loaded {len(df)} transactions")

    # Preprocess data
    print("\nPreprocessing data...")
    preprocessor = FraudDataPreprocessor()

    X_train, X_test, y_train, y_test = preprocessor.prepare_data_for_training(
        df,
        test_size=0.2,
        balance_method='smote',
        sampling_strategy='auto',
        scale=True
    )

    # Initialize trainer
    trainer = FraudModelTrainer()

    # Train all models
    trainer.train_all_models(X_train, y_train)

    # Evaluate all models
    trainer.evaluate_all_models(X_test, y_test)

    # Create visualizations
    trainer.compare_models()
    trainer.plot_roc_curves(X_test, y_test)
    trainer.plot_confusion_matrices(X_test, y_test)

    # Save models
    trainer.save_best_model()
    trainer.save_all_models()

    print("\n" + "=" * 80)
    print("MODEL TRAINING COMPLETE")
    print("=" * 80)
    print("\nAll models trained, evaluated, and saved!")
