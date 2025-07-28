"""
Model trainer for League of Legends win prediction.
Handles model training, evaluation, and feature importance analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import cross_val_score
from typing import Tuple, Dict, Any, List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from config import ML_CONFIG, MODELS_DIR, MODEL_FILE, SCALER_FILE, ENCODERS_FILE, FEATURE_COLUMNS_FILE, MODEL_STATS_FILE

logger = setup_logger(__name__)

class ModelTrainer:
    """Handles model training and evaluation."""
    
    def __init__(self):
        """Initialize the model trainer."""
        self.model = None
        self.feature_importance = None
        
    def train_model(self, X_train: np.ndarray, X_test: np.ndarray, 
                   y_train: np.ndarray, y_test: np.ndarray, 
                   feature_names: list) -> RandomForestClassifier:
        """
        Train a Random Forest model.
        
        Args:
            X_train: Training features
            X_test: Test features
            y_train: Training targets
            y_test: Test targets
            feature_names: List of feature names
            
        Returns:
            Trained RandomForestClassifier
        """
        logger.info("Training Random Forest model")
        
        # Initialize model
        self.model = RandomForestClassifier(
            n_estimators=ML_CONFIG['n_estimators'],
            max_depth=ML_CONFIG['max_depth'],
            min_samples_split=ML_CONFIG['min_samples_split'],
            min_samples_leaf=ML_CONFIG['min_samples_leaf'],
            random_state=ML_CONFIG['random_state'],
            class_weight=ML_CONFIG['class_weight']
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        self._evaluate_model(X_train, X_test, y_train, y_test)
        
        # Calculate feature importance
        self._calculate_feature_importance(feature_names)
        
        logger.info("Model training completed")
        return self.model
    
    def _evaluate_model(self, X_train: np.ndarray, X_test: np.ndarray,
                       y_train: np.ndarray, y_test: np.ndarray) -> None:
        """Evaluate the trained model."""
        logger.info("Evaluating model performance")
        
        # Calculate scores
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate ROC AUC
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        # Print results
        print(f"Train accuracy: {train_score:.3f}")
        print(f"Test accuracy: {test_score:.3f}")
        print(f"ROC AUC: {roc_auc:.3f}")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
        print(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Log results
        logger.info(f"Model evaluation - Train: {train_score:.3f}, Test: {test_score:.3f}, ROC AUC: {roc_auc:.3f}")
    
    def _calculate_feature_importance(self, feature_names: list) -> None:
        """Calculate and store feature importance."""
        if self.model is None:
            logger.error("No model available for feature importance calculation")
            return
        
        self.feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Feature importance calculated")
    
    def plot_feature_importance(self, top_n: int = 10) -> None:
        """Plot feature importance."""
        if self.feature_importance is None:
            logger.error("No feature importance data available")
            return
        
        plt.figure(figsize=(12, 8))
        top_features = self.feature_importance.head(top_n)
        
        sns.barplot(data=top_features, x='importance', y='feature')
        plt.title(f'Top {top_n} Most Important Features')
        plt.xlabel('Feature Importance')
        plt.ylabel('Feature')
        plt.tight_layout()
        plt.show()
        
        logger.info(f"Feature importance plot displayed (top {top_n} features)")
    
    def plot_confusion_matrix(self, X_test: np.ndarray, y_test: np.ndarray) -> None:
        """Plot confusion matrix."""
        if self.model is None:
            logger.error("No model available for confusion matrix")
            return
        
        y_pred = self.model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Loss', 'Win'], 
                   yticklabels=['Loss', 'Win'])
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.show()
        
        logger.info("Confusion matrix plot displayed")
    
    def plot_prediction_distribution(self, X: np.ndarray) -> None:
        """Plot distribution of predicted probabilities."""
        if self.model is None:
            logger.error("No model available for prediction distribution")
            return
        
        probabilities = self.model.predict_proba(X)[:, 1]
        
        plt.figure(figsize=(10, 6))
        plt.hist(probabilities, bins=20, edgecolor='black', alpha=0.7, color='skyblue')
        plt.title('Distribution of Predicted Win Probabilities')
        plt.xlabel('Win Probability')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.axvline(x=0.5, color='red', linestyle='--', label='Decision Threshold')
        plt.legend()
        plt.tight_layout()
        plt.show()
        
        logger.info("Prediction distribution plot displayed")
    
    def predict_win_probability(self, X: np.ndarray) -> np.ndarray:
        """
        Predict win probability for new data.
        
        Args:
            X: Features to predict on
            
        Returns:
            Array of win probabilities
        """
        if self.model is None:
            logger.error("No trained model available for prediction")
            return np.array([])
        
        probabilities = self.model.predict_proba(X)[:, 1]
        logger.info(f"Predicted win probabilities for {len(X)} samples")
        return probabilities
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get a summary of the trained model."""
        if self.model is None:
            return {"error": "No model available"}
        
        summary = {
            "model_type": "RandomForestClassifier",
            "n_estimators": self.model.n_estimators,
            "max_depth": self.model.max_depth,
            "feature_importance": self.feature_importance.to_dict('records') if self.feature_importance is not None else None
        }
        
        return summary
    
    def save_model(self, scaler=None, label_encoders=None, feature_columns=None) -> bool:
        """
        Save the trained model and preprocessing components.
        
        Args:
            scaler: Fitted StandardScaler
            label_encoders: Dictionary of fitted LabelEncoders
            feature_columns: List of feature column names
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure models directory exists
            MODELS_DIR.mkdir(exist_ok=True)
            
            # Save the model
            with open(MODEL_FILE, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved to {MODEL_FILE}")
            
            # Save scaler
            if scaler is not None:
                with open(SCALER_FILE, 'wb') as f:
                    pickle.dump(scaler, f)
                logger.info(f"Scaler saved to {SCALER_FILE}")
            
            # Save label encoders
            if label_encoders is not None:
                with open(ENCODERS_FILE, 'wb') as f:
                    pickle.dump(label_encoders, f)
                logger.info(f"Label encoders saved to {ENCODERS_FILE}")
            
            # Save feature columns
            if feature_columns is not None:
                with open(FEATURE_COLUMNS_FILE, 'w') as f:
                    json.dump(feature_columns, f)
                logger.info(f"Feature columns saved to {FEATURE_COLUMNS_FILE}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def save_model_statistics(self, X_train: np.ndarray, X_test: np.ndarray, 
                             y_train: np.ndarray, y_test: np.ndarray, 
                             data_summary: Dict[str, Any]) -> bool:
        """
        Save model performance statistics.
        
        Args:
            X_train, X_test, y_train, y_test: Training and test data
            data_summary: Summary of the dataset used for training
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from datetime import datetime
            import time
            
            # Calculate performance metrics
            train_accuracy = self.model.score(X_train, y_train)
            test_accuracy = self.model.score(X_test, y_test)
            
            # Cross-validation score
            cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            # ROC AUC score
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_pred_proba)
            
            # Feature importance
            feature_importance = self.model.feature_importances_
            top_features = np.argsort(feature_importance)[-5:]  # Top 5 features
            
            # Create statistics dictionary
            stats = {
                'timestamp': datetime.now().isoformat(),
                'model_version': f"v{int(time.time())}",
                'performance_metrics': {
                    'train_accuracy': float(train_accuracy),
                    'test_accuracy': float(test_accuracy),
                    'cross_validation_mean': float(cv_mean),
                    'cross_validation_std': float(cv_std),
                    'roc_auc_score': float(roc_auc)
                },
                'data_summary': data_summary,
                'model_info': {
                    'n_estimators': self.model.n_estimators,
                    'max_depth': self.model.max_depth,
                    'min_samples_split': self.model.min_samples_split,
                    'min_samples_leaf': self.model.min_samples_leaf,
                    'n_features': X_train.shape[1],
                    'n_samples_train': X_train.shape[0],
                    'n_samples_test': X_test.shape[0]
                },
                'feature_importance': {
                    'top_5_features': top_features.tolist(),
                    'importance_scores': feature_importance.tolist()
                }
            }
            
            # Load existing statistics or create new
            if MODEL_STATS_FILE.exists():
                with open(MODEL_STATS_FILE, 'r') as f:
                    all_stats = json.load(f)
            else:
                all_stats = []
            
            # Add new statistics
            all_stats.append(stats)
            
            # Save updated statistics
            with open(MODEL_STATS_FILE, 'w') as f:
                json.dump(all_stats, f, indent=2)
            
            logger.info(f"Model statistics saved to {MODEL_STATS_FILE}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model statistics: {e}")
            return False
    
    def load_model_statistics(self) -> List[Dict[str, Any]]:
        """
        Load all model statistics.
        
        Returns:
            List of model statistics dictionaries
        """
        try:
            if MODEL_STATS_FILE.exists():
                with open(MODEL_STATS_FILE, 'r') as f:
                    stats = json.load(f)
                logger.info(f"Loaded {len(stats)} model statistics records")
                return stats
            else:
                logger.info("No model statistics file found")
                return []
                
        except Exception as e:
            logger.error(f"Error loading model statistics: {e}")
            return []
    
    def get_latest_model_statistics(self) -> Dict[str, Any]:
        """
        Get the most recent model statistics.
        
        Returns:
            Latest model statistics dictionary or empty dict if none found
        """
        stats = self.load_model_statistics()
        if stats:
            return stats[-1]  # Return the most recent
        return {}
    
    def print_model_statistics(self) -> None:
        """
        Print a summary of model statistics.
        """
        stats = self.load_model_statistics()
        
        if not stats:
            print("No model statistics available.")
            return
        
        print("\n📊 Model Performance Statistics")
        print("=" * 50)
        
        for i, stat in enumerate(stats[-3:], 1):  # Show last 3 models
            print(f"\nModel Version {i}: {stat['model_version']}")
            print(f"Training Date: {stat['timestamp']}")
            
            metrics = stat['performance_metrics']
            print(f"  Test Accuracy: {metrics['test_accuracy']:.3f}")
            print(f"  Train Accuracy: {metrics['train_accuracy']:.3f}")
            print(f"  Cross-Validation: {metrics['cross_validation_mean']:.3f} ± {metrics['cross_validation_std']:.3f}")
            print(f"  ROC AUC: {metrics['roc_auc_score']:.3f}")
            
            data_summary = stat['data_summary']
            print(f"  Data: {data_summary.get('total_matches', 'N/A')} matches, {data_summary.get('unique_players', 'N/A')} players")
            
            model_info = stat['model_info']
            print(f"  Features: {model_info['n_features']}, Samples: {model_info['n_samples_train']} train, {model_info['n_samples_test']} test")
    
    def load_model(self) -> bool:
        """
        Load a previously saved model and preprocessing components.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if model file exists
            if not MODEL_FILE.exists():
                logger.warning(f"Model file not found at {MODEL_FILE}")
                return False
            
            # Load the model
            with open(MODEL_FILE, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded from {MODEL_FILE}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def load_preprocessing_components(self) -> Tuple[Any, Dict, List]:
        """
        Load preprocessing components (scaler, encoders, feature columns).
        
        Returns:
            Tuple of (scaler, label_encoders, feature_columns) or (None, None, None) if failed
        """
        try:
            scaler = None
            label_encoders = None
            feature_columns = None
            
            # Load scaler
            if SCALER_FILE.exists():
                with open(SCALER_FILE, 'rb') as f:
                    scaler = pickle.load(f)
                logger.info(f"Scaler loaded from {SCALER_FILE}")
            
            # Load label encoders
            if ENCODERS_FILE.exists():
                with open(ENCODERS_FILE, 'rb') as f:
                    label_encoders = pickle.load(f)
                logger.info(f"Label encoders loaded from {ENCODERS_FILE}")
            
            # Load feature columns
            if FEATURE_COLUMNS_FILE.exists():
                with open(FEATURE_COLUMNS_FILE, 'r') as f:
                    feature_columns = json.load(f)
                logger.info(f"Feature columns loaded from {FEATURE_COLUMNS_FILE}")
            
            return scaler, label_encoders, feature_columns
            
        except Exception as e:
            logger.error(f"Error loading preprocessing components: {e}")
            return None, None, None
    
    def incremental_train(self, X_new: np.ndarray, y_new: np.ndarray) -> bool:
        """
        Incrementally train the model with new data.
        
        Args:
            X_new: New training features
            y_new: New training targets
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.model is None:
                logger.error("No model available for incremental training")
                return False
            
            # Combine new data with existing model
            # Note: RandomForest doesn't support true incremental learning,
            # so we retrain with combined data
            logger.info("Performing incremental training with new data")
            
            # Get existing training data from the model (if available)
            # For now, we'll just retrain with the new data
            self.model.fit(X_new, y_new)
            
            logger.info("Incremental training completed")
            return True
            
        except Exception as e:
            logger.error(f"Error in incremental training: {e}")
            return False 