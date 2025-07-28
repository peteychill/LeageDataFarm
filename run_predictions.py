#!/usr/bin/env python3
"""
Simple script to run predictions using the saved model.
Usage: python run_predictions.py
"""

import pandas as pd
import numpy as np
from ml.ml_pipeline import MLPipeline
from config import LEAGUE_MATCHES_CSV

def main():
    """Run predictions using the saved model."""
    print("🎮 League Data Farm - Prediction Runner")
    print("=" * 50)
    
    try:
        # Load the saved model
        pipeline = MLPipeline()
        
        if pipeline.load_existing_model():
            print("✅ Model loaded successfully!")
        else:
            print("❌ No saved model found. Please train a model first.")
            return
        
        # Load data for predictions
        print("\n📊 Loading data for predictions...")
        df = pd.read_csv(LEAGUE_MATCHES_CSV)
        
        if df.empty:
            print("❌ No data available for predictions")
            return
        
        print(f"✅ Loaded {len(df)} matches from {df['player_name'].nunique()} players")
        
        # Make predictions on a sample
        print("\n🎯 Making predictions...")
        sample_size = min(10, len(df))  # Use up to 10 matches
        sample_data = df.head(sample_size)
        
        probabilities = pipeline.predict_with_saved_model(sample_data)
        
        print(f"✅ Made predictions on {len(sample_data)} matches")
        print("\n📈 Prediction Results:")
        print("-" * 40)
        
        for i, (_, match) in enumerate(sample_data.iterrows()):
            prob = probabilities[i]
            predicted_win = "WIN" if prob > 0.5 else "LOSS"
            confidence = max(prob, 1 - prob) * 100
            
            print(f"Match {i+1}: {match['player_name']} ({match['championName']} - {match['role']})")
            print(f"  Prediction: {predicted_win} ({prob:.1%})")
            print(f"  Confidence: {confidence:.1f}%")
            print(f"  Actual: {'WIN' if match['win'] else 'LOSS'}")
            print()
        
        # Show overall statistics
        print("📊 Overall Statistics:")
        print("-" * 40)
        print(f"Average win probability: {np.mean(probabilities):.1%}")
        print(f"Predicted wins: {np.sum(probabilities > 0.5)}/{len(probabilities)}")
        print(f"Actual wins in sample: {np.sum(sample_data['win'])}/{len(sample_data)}")
        
    except Exception as e:
        print(f"❌ Error running predictions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 