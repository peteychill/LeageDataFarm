# Model Persistence Guide

## 🎯 Overview

The League Data Farm system now supports **model persistence**, allowing you to:

- ✅ **Save trained models** for later use
- ✅ **Load existing models** without retraining
- ✅ **Incrementally train** with new data
- ✅ **Make predictions** with saved models
- ✅ **Automatic model updates** as new data becomes available

## 📁 Model Storage

Models are automatically saved to the `models/` directory:

```
models/
├── league_win_predictor.pkl    # Trained Random Forest model
├── feature_scaler.pkl          # Fitted StandardScaler
├── label_encoders.pkl          # Fitted LabelEncoders
└── feature_columns.json        # Feature column names
```

## 🚀 Usage Examples

### 1. Train and Save Model

```python
from ml.ml_pipeline import MLPipeline

# Train and save model
pipeline = MLPipeline()
results = pipeline.run_full_pipeline(
    update_data=True,    # Collect new data
    save_model=True,     # Save the model
    load_existing=False  # Don't load existing
)

print(f"Model saved with {results['data_summary']['total_matches']} matches")
```

### 2. Load Existing Model

```python
# Load without retraining
pipeline = MLPipeline()
if pipeline.load_existing_model():
    print("✓ Model loaded successfully!")
else:
    print("✗ No saved model found")
```

### 3. Make Predictions with Saved Model

```python
import pandas as pd

# Load new data for predictions
new_data = pd.read_csv('new_matches.csv')

# Make predictions using saved model
probabilities = pipeline.predict_with_saved_model(new_data)
print(f"Win probabilities: {probabilities}")
```

### 4. Incremental Training

```python
# Train with new data without full retraining
new_data = pd.read_csv('new_matches.csv')
results = pipeline.incremental_train_with_new_data(
    new_data=new_data,
    save_model=True  # Save updated model
)

print(f"Trained with {results['new_data_samples']} new samples")
```

## 🔄 Workflow Examples

### Daily Data Collection and Model Updates

```python
from ml.ml_pipeline import MLPipeline
from data_collection.data_collector import DataCollector

# 1. Collect new data
collector = DataCollector()
df = collector.update_csv()

# 2. Load existing model
pipeline = MLPipeline()
if pipeline.load_existing_model():
    # 3. Incrementally train with new data
    results = pipeline.incremental_train_with_new_data(df, save_model=True)
    print(f"Model updated with {len(df)} new matches")
else:
    # 4. Train new model if none exists
    results = pipeline.run_full_pipeline(save_model=True)
    print("New model trained and saved")
```

### Production Prediction Service

```python
from ml.ml_pipeline import MLPipeline
import pandas as pd

# Load saved model once
pipeline = MLPipeline()
pipeline.load_existing_model()

# Make predictions on new matches
def predict_match_win(match_data):
    """Predict win probability for a single match."""
    df = pd.DataFrame([match_data])
    probability = pipeline.predict_with_saved_model(df)[0]
    return probability

# Example usage
match_data = {
    'championName': 'Yasuo',
    'role': 'MIDDLE',
    'kills': 8,
    'deaths': 3,
    'assists': 5,
    # ... other features
}

win_probability = predict_match_win(match_data)
print(f"Win probability: {win_probability:.2%}")
```

## 📊 Model Management

### Check Model Status

```python
import os
from config import MODEL_FILE, SCALER_FILE, ENCODERS_FILE

def check_model_status():
    """Check if all model components exist."""
    components = {
        'Model': MODEL_FILE,
        'Scaler': SCALER_FILE,
        'Encoders': ENCODERS_FILE
    }
    
    for name, path in components.items():
        if path.exists():
            size = path.stat().st_size / 1024  # KB
            print(f"✓ {name}: {size:.1f} KB")
        else:
            print(f"✗ {name}: Not found")
    
    return all(path.exists() for path in components.values())

# Usage
if check_model_status():
    print("All model components available")
else:
    print("Some model components missing")
```

### Model Versioning

```python
import shutil
from datetime import datetime
from config import MODELS_DIR

def backup_model(version_name=None):
    """Create a backup of the current model."""
    if version_name is None:
        version_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backup_dir = MODELS_DIR / f"backup_{version_name}"
    backup_dir.mkdir(exist_ok=True)
    
    # Copy model files
    model_files = ['league_win_predictor.pkl', 'feature_scaler.pkl', 
                   'label_encoders.pkl', 'feature_columns.json']
    
    for file in model_files:
        src = MODELS_DIR / file
        dst = backup_dir / file
        if src.exists():
            shutil.copy2(src, dst)
    
    print(f"Model backed up to {backup_dir}")
    return backup_dir

# Usage
backup_path = backup_model("v1.0")
```

## 🔧 Advanced Configuration

### Custom Model Paths

```python
# In config.py, you can customize model paths:
MODELS_DIR = PROJECT_ROOT / 'models' / 'production'
MODEL_FILE = MODELS_DIR / 'league_win_predictor_v2.pkl'
```

### Model Performance Tracking

```python
import json
from datetime import datetime

def log_model_performance(accuracy, data_size, model_version="latest"):
    """Log model performance metrics."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'model_version': model_version,
        'accuracy': accuracy,
        'data_size': data_size
    }
    
    log_file = MODELS_DIR / 'performance_log.json'
    
    # Load existing log or create new
    if log_file.exists():
        with open(log_file, 'r') as f:
            log = json.load(f)
    else:
        log = []
    
    log.append(log_entry)
    
    # Save updated log
    with open(log_file, 'w') as f:
        json.dump(log, f, indent=2)
    
    print(f"Performance logged: {accuracy:.3f} accuracy")

# Usage
log_model_performance(0.75, 1000, "v1.2")
```

## 🚨 Best Practices

### 1. Regular Backups
```python
# Create backups before major updates
backup_model("before_incremental_update")
```

### 2. Model Validation
```python
def validate_model(pipeline, test_data):
    """Validate model performance on test data."""
    predictions = pipeline.predict_with_saved_model(test_data)
    # Add your validation logic here
    return True
```

### 3. Error Handling
```python
try:
    pipeline.load_existing_model()
except Exception as e:
    print(f"Error loading model: {e}")
    # Fallback to training new model
    pipeline.run_full_pipeline(save_model=True)
```

### 4. Performance Monitoring
```python
import time

def timed_prediction(pipeline, data):
    """Time prediction performance."""
    start_time = time.time()
    predictions = pipeline.predict_with_saved_model(data)
    end_time = time.time()
    
    print(f"Predictions completed in {end_time - start_time:.3f} seconds")
    return predictions
```

## 📈 Benefits

### Time Savings
- **No retraining**: Load saved models instantly
- **Faster predictions**: Skip preprocessing setup
- **Incremental updates**: Train only on new data

### Resource Efficiency
- **Reduced computation**: Avoid full retraining
- **Memory efficient**: Load only when needed
- **Scalable**: Handle large datasets incrementally

### Production Ready
- **Reliable**: Robust error handling
- **Versioned**: Model backup and recovery
- **Monitored**: Performance tracking
- **Deployable**: Easy integration into services

## 🔄 Migration from Non-Persistent

If you're upgrading from the previous version:

1. **Train initial model**:
   ```python
   pipeline = MLPipeline()
   results = pipeline.run_full_pipeline(save_model=True)
   ```

2. **Update existing code**:
   ```python
   # Old way
   pipeline = MLPipeline()
   results = pipeline.run_full_pipeline()
   
   # New way
   pipeline = MLPipeline()
   if pipeline.load_existing_model():
       # Use saved model
       predictions = pipeline.predict_with_saved_model(data)
   else:
       # Train new model
       results = pipeline.run_full_pipeline(save_model=True)
   ```

3. **Set up automated updates**:
   ```python
   # Daily script
   new_data = collect_daily_data()
   pipeline.incremental_train_with_new_data(new_data, save_model=True)
   ```

This model persistence system makes your League Data Farm project **production-ready** and **scalable** for real-world applications! 🚀 