"""
Complete Machine Learning pipeline for League of Legends win prediction.
Combines data collection, feature engineering, and model training.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from config import LEAGUE_MATCHES_CSV
from data_collection.data_collector import DataCollector
from ml.feature_engineering import FeatureEngineer
from ml.model_trainer import ModelTrainer

logger = setup_logger(__name__)

class MLPipeline:
    """Complete ML pipeline for League of Legends win prediction."""
    
    def __init__(self):
        """Initialize the ML pipeline."""
        self.data_collector = DataCollector()
        self.feature_engineer = FeatureEngineer()
        self.model_trainer = ModelTrainer()
        self.trained_model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_columns = None
        
    def run_full_pipeline(self, update_data: bool = True, save_model: bool = True, load_existing: bool = False) -> Dict[str, Any]:
        """
        Run the complete ML pipeline.
        
        Args:
            update_data: Whether to collect new data or use existing data
            save_model: Whether to save the trained model
            load_existing: Whether to try loading existing model first
            
        Returns:
            Dictionary containing pipeline results
        """
        logger.info("Starting complete ML pipeline")
        
        try:
            # Step 1: Data Collection
            if update_data:
                logger.info("Collecting new data...")
                df = self.data_collector.update_csv()
            else:
                logger.info("Loading existing data...")
                df = pd.read_csv(LEAGUE_MATCHES_CSV)
            
            if df.empty:
                raise ValueError("No data available for training")
            
            logger.info(f"Loaded {len(df)} matches from {df['player_name'].nunique()} players")
            
            # Step 2: Try to load existing model if requested
            if load_existing and self.model_trainer.load_model():
                logger.info("Loaded existing model successfully")
                # Load preprocessing components
                self.feature_engineer.load_preprocessing_components()
                scaler, label_encoders, feature_columns = self.model_trainer.load_preprocessing_components()
                if scaler and label_encoders and feature_columns:
                    self.scaler = scaler
                    self.label_encoders = label_encoders
                    self.feature_columns = feature_columns
                    logger.info("Loaded existing preprocessing components")
                    return self._create_results_summary(df, None, None, None, None)
            
            # Step 3: Feature Engineering
            logger.info("Performing feature engineering...")
            (X_scaled, X_train, X_test, y_train, y_test, 
             self.scaler, self.label_encoders, self.feature_columns) = self.feature_engineer.prepare_data_for_ml(df)
            
            # Step 4: Model Training
            logger.info("Training model...")
            self.trained_model = self.model_trainer.train_model(
                X_train, X_test, y_train, y_test, self.feature_columns
            )
            
            # Step 5: Save model and preprocessing components if requested
            if save_model:
                logger.info("Saving model and preprocessing components...")
                self.model_trainer.save_model(
                    scaler=self.scaler,
                    label_encoders=self.label_encoders,
                    feature_columns=self.feature_columns
                )
                self.feature_engineer.save_preprocessing_components()
                
                # Save model statistics
                logger.info("Saving model statistics...")
                results = self._create_results_summary(df, X_train, X_test, y_train, y_test)
                self.model_trainer.save_model_statistics(X_train, X_test, y_train, y_test, results['data_summary'])
            
            # Step 6: Generate Visualizations
            logger.info("Generating visualizations...")
            self._generate_visualizations(X_test, y_test, X_scaled)
            
            # Step 7: Create Results Summary
            results = self._create_results_summary(df, X_train, X_test, y_train, y_test)
            
            logger.info("ML pipeline completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
    
    def _generate_visualizations(self, X_test: np.ndarray, y_test: np.ndarray, 
                               X_scaled: np.ndarray) -> None:
        """Generate all visualizations."""
        try:
            # Feature importance
            self.model_trainer.plot_feature_importance()
            
            # Confusion matrix
            self.model_trainer.plot_confusion_matrix(X_test, y_test)
            
            # Prediction distribution
            self.model_trainer.plot_prediction_distribution(X_scaled)
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
    
    def _create_results_summary(self, df: pd.DataFrame, X_train: np.ndarray, 
                              X_test: np.ndarray, y_train: np.ndarray, 
                              y_test: np.ndarray) -> Dict[str, Any]:
        """Create a comprehensive results summary."""
        summary = {
            "data_summary": {
                "total_matches": len(df),
                "unique_players": df['player_name'].nunique(),
                "unique_champions": df['championName'].nunique(),
                "win_rate": df['win'].mean(),
                "train_samples": len(X_train),
                "test_samples": len(X_test)
            },
            "model_summary": self.model_trainer.get_model_summary(),
            "feature_importance": self.model_trainer.feature_importance.to_dict('records') if self.model_trainer.feature_importance is not None else None
        }
        
        return summary
    
    def predict_new_matches(self, new_data: pd.DataFrame) -> np.ndarray:
        """
        Predict win probabilities for new match data.
        
        Args:
            new_data: DataFrame with new match data
            
        Returns:
            Array of win probabilities
        """
        if self.trained_model is None:
            raise ValueError("No trained model available. Run the pipeline first.")
        
        # Transform new data using fitted preprocessing
        X_transformed = self.feature_engineer.transform_new_data(new_data)
        
        # Make predictions
        probabilities = self.model_trainer.predict_win_probability(X_transformed)
        
        return probabilities
    
    def get_feature_importance(self, top_n: int = 10) -> pd.DataFrame:
        """Get feature importance as a DataFrame."""
        if self.model_trainer.feature_importance is None:
            raise ValueError("No feature importance available. Train a model first.")
        
        return self.model_trainer.feature_importance.head(top_n)
    
    def load_existing_model(self) -> bool:
        """
        Load an existing trained model and preprocessing components.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the model
            if not self.model_trainer.load_model():
                return False
            
            # Load preprocessing components
            if not self.feature_engineer.load_preprocessing_components():
                return False
            
            # Set the trained model
            self.trained_model = self.model_trainer.model
            
            logger.info("Successfully loaded existing model and preprocessing components")
            return True
            
        except Exception as e:
            logger.error(f"Error loading existing model: {e}")
            return False
    
    def incremental_train_with_new_data(self, new_data: pd.DataFrame, save_model: bool = True) -> Dict[str, Any]:
        """
        Incrementally train the model with new data.
        
        Args:
            new_data: New data to add to training
            save_model: Whether to save the updated model
            
        Returns:
            Dictionary containing training results
        """
        try:
            logger.info("Starting incremental training with new data")
            
            # Load existing model if available
            if not self.load_existing_model():
                logger.warning("No existing model found, training new model")
                return self.run_full_pipeline(update_data=False, save_model=save_model)
            
            # Transform new data using existing preprocessing
            X_new = self.feature_engineer.transform_new_data(new_data)
            
            # Get target variable from new data
            y_new = new_data['win'].values
            
            # Perform incremental training
            success = self.model_trainer.incremental_train(X_new, y_new)
            
            if success and save_model:
                # Save updated model
                self.model_trainer.save_model(
                    scaler=self.scaler,
                    label_encoders=self.label_encoders,
                    feature_columns=self.feature_columns
                )
                self.feature_engineer.save_preprocessing_components()
                logger.info("Updated model saved successfully")
            
            # Create results summary
            results = {
                "incremental_training": True,
                "new_data_samples": len(new_data),
                "model_updated": success,
                "model_saved": save_model
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in incremental training: {e}")
            raise
    
    def predict_with_saved_model(self, new_data: pd.DataFrame) -> np.ndarray:
        """
        Make predictions using a saved model without retraining.
        
        Args:
            new_data: New data to predict on
            
        Returns:
            Array of win probabilities
        """
        try:
            # Load existing model if not already loaded
            if self.trained_model is None:
                if not self.load_existing_model():
                    raise ValueError("No saved model available")
            
            # Transform new data using saved preprocessing
            X_transformed = self.feature_engineer.transform_new_data(new_data)
            
            # Make predictions
            probabilities = self.model_trainer.predict_win_probability(X_transformed)
            
            return probabilities
            
        except Exception as e:
            logger.error(f"Error making predictions with saved model: {e}")
            raise

def main():
    """Main function to run the ML pipeline."""
    try:
        pipeline = MLPipeline()
        results = pipeline.run_full_pipeline(update_data=True)
        
        print("\n" + "="*50)
        print("ML PIPELINE RESULTS")
        print("="*50)
        
        # Data Summary
        print(f"\nData Summary:")
        print(f"  Total matches: {results['data_summary']['total_matches']}")
        print(f"  Unique players: {results['data_summary']['unique_players']}")
        print(f"  Unique champions: {results['data_summary']['unique_champions']}")
        print(f"  Overall win rate: {results['data_summary']['win_rate']:.2%}")
        print(f"  Training samples: {results['data_summary']['train_samples']}")
        print(f"  Test samples: {results['data_summary']['test_samples']}")
        
        # Model Summary
        print(f"\nModel Summary:")
        print(f"  Model type: {results['model_summary']['model_type']}")
        print(f"  N estimators: {results['model_summary']['n_estimators']}")
        print(f"  Max depth: {results['model_summary']['max_depth']}")
        
        # Top Features
        if results['feature_importance']:
            print(f"\nTop 5 Most Important Features:")
            for i, feature in enumerate(results['feature_importance'][:5], 1):
                print(f"  {i}. {feature['feature']}: {feature['importance']:.4f}")
        
        print("\nPipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise

if __name__ == "__main__":
    main() 