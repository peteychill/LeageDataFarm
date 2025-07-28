#!/usr/bin/env python3
"""
Demo script showcasing model persistence features.
Shows how to save, load, and incrementally train models.
"""

import pandas as pd
from ml.ml_pipeline import MLPipeline
from utils.logger import setup_logger

logger = setup_logger(__name__)

def demo_model_persistence():
    """Demonstrate model persistence features."""
    
    print("=" * 60)
    print("LEAGUE DATA FARM - MODEL PERSISTENCE DEMO")
    print("=" * 60)
    
    pipeline = MLPipeline()
    
    # Step 1: Train and save initial model
    print("\n1. Training initial model...")
    try:
        results = pipeline.run_full_pipeline(
            update_data=False,  # Collect new data
            save_model=True,   # Save the model
            load_existing=True # Don't load existing
        )
        
        print(f"✓ Initial model trained and saved!")
        print(f"  - Total matches: {results['data_summary']['total_matches']}")
        print(f"  - Model accuracy: {results['model_summary']['model_type']}")
        
    except Exception as e:
        print(f"✗ Error training initial model: {e}")
        return
    
    # Step 2: Load existing model without retraining
    print("\n2. Loading existing model...")
    try:
        if pipeline.load_existing_model():
            print("✓ Existing model loaded successfully!")
        else:
            print("✗ No existing model found")
            return
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return
    
    # Step 3: Make predictions with loaded model
    print("\n3. Making predictions with loaded model...")
    try:
        # Load some existing data for demonstration
        from config import LEAGUE_MATCHES_CSV
        df = pd.read_csv(LEAGUE_MATCHES_CSV)
        
        if not df.empty:
            # Use a small sample for prediction
            sample_data = df.head(5)
            probabilities = pipeline.predict_with_saved_model(sample_data)
            
            print("✓ Predictions made successfully!")
            print(f"  - Sample size: {len(sample_data)}")
            print(f"  - Win probabilities: {probabilities[:3]}...")  # Show first 3
        else:
            print("✗ No data available for predictions")
            
    except Exception as e:
        print(f"✗ Error making predictions: {e}")
    
    # Step 4: Demonstrate incremental training
    print("\n4. Demonstrating incremental training...")
    try:
        # Simulate new data (in practice, this would be fresh data from API)
        from config import LEAGUE_MATCHES_CSV
        df = pd.read_csv(LEAGUE_MATCHES_CSV)
        
        if not df.empty:
            # Use a small sample as "new" data
            new_data = df.tail(10)  # Last 10 rows as "new" data
            
            results = pipeline.incremental_train_with_new_data(new_data, save_model=True)
            
            print("✓ Incremental training completed!")
            print(f"  - New data samples: {results['new_data_samples']}")
            print(f"  - Model updated: {results['model_updated']}")
            print(f"  - Model saved: {results['model_saved']}")
        else:
            print("✗ No data available for incremental training")
            
    except Exception as e:
        print(f"✗ Error in incremental training: {e}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED!")
    print("=" * 60)
    print("\nModel persistence features demonstrated:")
    print("✓ Model saving and loading")
    print("✓ Prediction with saved models")
    print("✓ Incremental training with new data")
    print("✓ Automatic model updates")
    
    print("\nNext steps:")
    print("1. Run regular data collection: python run_data_collection.py")
    print("2. Use saved model for predictions")
    print("3. Incrementally train with new data as it becomes available")

if __name__ == "__main__":
    demo_model_persistence() 