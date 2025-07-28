"""
Feature engineering for League of Legends match data.
Handles data preprocessing, feature creation, and scaling.
"""

import pandas as pd
import numpy as np
import pickle
import json
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict, List, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from config import FEATURE_COLUMNS, ML_CONFIG, SCALER_FILE, ENCODERS_FILE, FEATURE_COLUMNS_FILE

logger = setup_logger(__name__)

class FeatureEngineer:
    """Handles feature engineering and preprocessing for ML models."""
    
    def __init__(self):
        """Initialize the feature engineer."""
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = FEATURE_COLUMNS.copy()
        
    def prepare_data_for_ml(self, df: pd.DataFrame, target_variable: str = 'win') -> Tuple:
        """
        Prepare data for machine learning.
        
        Args:
            df: Raw DataFrame
            target_variable: Target variable column name
            
        Returns:
            Tuple of (X_scaled, X_train, X_test, y_train, y_test, scaler, label_encoders, features)
        """
        logger.info("Starting feature engineering process")
        
        # Create copy of dataframe
        df_ml = df.copy()
        
        # Convert gameDuration from HH:MM:SS to total seconds
        df_ml['gameDuration'] = df_ml['gameDuration'].apply(self._duration_to_seconds)
        
        # Create derived features
        df_ml = self._create_derived_features(df_ml)
        
        # Encode categorical variables
        df_ml = self._encode_categorical_variables(df_ml)
        
        # Select and prepare features
        X, y = self._prepare_features_and_target(df_ml, target_variable)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, 
            test_size=ML_CONFIG['test_size'], 
            random_state=ML_CONFIG['random_state'], 
            stratify=y
        )
        
        logger.info(f"Feature engineering completed. Train: {len(X_train)}, Test: {len(X_test)}")
        
        return X_scaled, X_train, X_test, y_train, y_test, self.scaler, self.label_encoders, self.feature_columns
    
    def _duration_to_seconds(self, duration_str: str) -> int:
        """Convert HH:MM:SS format to total seconds."""
        try:
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            else:
                return 0
        except:
            return 0
    
    def _create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features from raw data."""
        logger.info("Creating derived features")
        
        # KDA ratio
        df['kda'] = (df['kills'] + df['assists']) / (df['deaths'] + 1)
        
        # Damage per minute
        df['damage_per_min'] = df['totalDamageDealtToChampions'] / (df['gameDuration'] / 60)
        
        # Vision per minute
        df['vision_per_min'] = df['visionScore'] / (df['gameDuration'] / 60)
        
        # Gold efficiency (gold earned per minute)
        df['gold_efficiency'] = df['goldEarned'] / (df['gameDuration'] / 60)
        
        # CS per minute
        df['cs_per_min'] = df['totalMinionsKilled'] / (df['gameDuration'] / 60)
        
        # Damage taken per minute
        df['damage_taken_per_min'] = df['totalDamageTaken'] / (df['gameDuration'] / 60)
        
        # Team fight participation (kill participation * team damage percentage)
        df['team_fight_participation'] = df['killParticipation'] * df['teamDamagePercentage']
        
        logger.info("Derived features created")
        return df
    
    def _encode_categorical_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables using LabelEncoder."""
        logger.info("Encoding categorical variables")
        
        categorical_columns = ['championName', 'role']
        
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
                logger.info(f"Encoded {col} with {len(le.classes_)} unique values")
        
        return df
    
    def _prepare_features_and_target(self, df: pd.DataFrame, target_variable: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target variables."""
        logger.info("Preparing features and target")
        
        # Ensure all feature columns exist
        missing_features = [col for col in self.feature_columns if col not in df.columns]
        if missing_features:
            logger.warning(f"Missing features: {missing_features}")
            # Remove missing features from the list
            self.feature_columns = [col for col in self.feature_columns if col in df.columns]
        
        # Select features and target
        X = df[self.feature_columns].fillna(0)  # Fill NaN with 0
        y = df[target_variable]
        
        logger.info(f"Selected {len(self.feature_columns)} features")
        return X, y
    
    def transform_new_data(self, new_data: pd.DataFrame) -> np.ndarray:
        """
        Transform new data using fitted encoders and scaler.
        
        Args:
            new_data: New data to transform
            
        Returns:
            Transformed data array
        """
        # Apply the same preprocessing steps
        new_data = new_data.copy()
        new_data['gameDuration'] = new_data['gameDuration'].apply(self._duration_to_seconds)
        new_data = self._create_derived_features(new_data)
        
        # Encode categorical variables using fitted encoders
        for col, le in self.label_encoders.items():
            if col in new_data.columns:
                # Handle unseen categories
                new_data[col] = new_data[col].astype(str).map(
                    lambda x: x if x in le.classes_ else le.classes_[0]
                )
                new_data[col] = le.transform(new_data[col])
        
        # Select features and fill missing values
        X = new_data[self.feature_columns].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        return X_scaled 
    
    def save_preprocessing_components(self) -> bool:
        """
        Save preprocessing components (scaler, encoders, feature columns).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Save scaler
            with open(SCALER_FILE, 'wb') as f:
                pickle.dump(self.scaler, f)
            logger.info(f"Scaler saved to {SCALER_FILE}")
            
            # Save label encoders
            with open(ENCODERS_FILE, 'wb') as f:
                pickle.dump(self.label_encoders, f)
            logger.info(f"Label encoders saved to {ENCODERS_FILE}")
            
            # Save feature columns
            with open(FEATURE_COLUMNS_FILE, 'w') as f:
                json.dump(self.feature_columns, f)
            logger.info(f"Feature columns saved to {FEATURE_COLUMNS_FILE}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving preprocessing components: {e}")
            return False
    
    def load_preprocessing_components(self) -> bool:
        """
        Load preprocessing components (scaler, encoders, feature columns).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load scaler
            if SCALER_FILE.exists():
                with open(SCALER_FILE, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info(f"Scaler loaded from {SCALER_FILE}")
            
            # Load label encoders
            if ENCODERS_FILE.exists():
                with open(ENCODERS_FILE, 'rb') as f:
                    self.label_encoders = pickle.load(f)
                logger.info(f"Label encoders loaded from {ENCODERS_FILE}")
            
            # Load feature columns
            if FEATURE_COLUMNS_FILE.exists():
                with open(FEATURE_COLUMNS_FILE, 'r') as f:
                    self.feature_columns = json.load(f)
                logger.info(f"Feature columns loaded from {FEATURE_COLUMNS_FILE}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading preprocessing components: {e}")
            return False 