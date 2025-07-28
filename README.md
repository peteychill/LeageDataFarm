# League Data Farm

A comprehensive machine learning project for predicting League of Legends match outcomes using Riot Games API data.

## 🚀 Features

- **Automated Data Collection**: Fetches match data from Riot Games API
- **Feature Engineering**: Creates derived features for better ML performance
- **Machine Learning Pipeline**: Complete pipeline from data to predictions
- **Model Persistence**: Save, load, and incrementally train models
- **Visualization**: Comprehensive plots and analysis
- **Error Handling**: Robust error handling and logging
- **Configuration Management**: Centralized configuration

## 📁 Project Structure

```
LeagueDataFarm/
├── config.py                 # Centralized configuration
├── requirements.txt          # Python dependencies
├── run_data_collection.py   # Data collection script
├── run_ml_pipeline.py       # ML pipeline script
├── run_model_persistence_demo.py # Model persistence demo
├── data_collection/         # Data collection modules
│   ├── __init__.py
│   ├── riot_api.py          # Riot API client
│   ├── data_processor.py    # Data processing utilities
│   └── data_collector.py    # Main data collector
├── ml/                      # Machine learning modules
│   ├── __init__.py
│   ├── feature_engineering.py # Feature engineering
│   ├── model_trainer.py     # Model training and evaluation
│   └── ml_pipeline.py       # Complete ML pipeline
├── utils/                   # Utility modules
│   ├── __init__.py
│   └── logger.py            # Logging utilities
├── docs/                    # 📚 Documentation
│   ├── README.md            # Documentation index
│   ├── TIMESTAMP_FILTERING_GUIDE.md
│   ├── MODEL_PERSISTENCE_GUIDE.md
│   └── OPTIMIZATION_SUMMARY.md
├── models/                  # Saved models (created automatically)
│   ├── league_win_predictor.pkl    # Trained model
│   ├── feature_scaler.pkl          # Feature scaler
│   ├── label_encoders.pkl          # Label encoders
│   ├── feature_columns.json        # Feature column names
│   └── model_statistics.json       # Model performance tracking
├── Data/                    # Data storage
│   ├── summonerNames.txt    # Summoner names and tags
│   └── league_matches.csv   # Collected match data
└── PythonFiles/             # Legacy files (can be removed)
    └── GrabData.py
```

## 📚 Documentation

For detailed guides and documentation, see the [docs/](./docs/) folder:

- **[📖 Documentation Index](./docs/README.md)** - Overview of all documentation
- **[⏰ Timestamp Filtering Guide](./docs/TIMESTAMP_FILTERING_GUIDE.md)** - Avoid duplicate data collection
- **[💾 Model Persistence Guide](./docs/MODEL_PERSISTENCE_GUIDE.md)** - Save and load trained models
- **[🚀 Optimization Summary](./docs/OPTIMIZATION_SUMMARY.md)** - Project evolution and architecture

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `dev.env` file in the parent directory with your Riot API key:

```env
RIOT_API_KEY=your_riot_api_key_here
```

### 3. Configure Summoner Names

Edit `Data/summonerNames.txt` with summoner names and tags:

```
summonerName:tag
anotherSummoner:tag2
```

## 🚀 Usage

### Data Collection Only

```bash
# Collect new data with timestamp filtering (default)
python run_data_collection.py

# Collect all available data without timestamp filtering
python run_data_collection.py --no-timestamp-filtering
```

### Complete ML Pipeline

```bash
python run_ml_pipeline.py
```

### Using in Jupyter Notebooks

```python
from ml.ml_pipeline import MLPipeline

# Run complete pipeline
pipeline = MLPipeline()
results = pipeline.run_full_pipeline(update_data=True)

# Make predictions on new data
probabilities = pipeline.predict_new_matches(new_data)
```

## 🔄 Model Persistence

The system supports saving, loading, and incrementally training models:

### Save and Load Models

```python
from ml.ml_pipeline import MLPipeline

# Train and save model
pipeline = MLPipeline()
results = pipeline.run_full_pipeline(save_model=True)

# Load existing model without retraining
pipeline.load_existing_model()

# Make predictions with saved model
probabilities = pipeline.predict_with_saved_model(new_data)
```

### Incremental Training

```python
# Train with new data without full retraining
new_data = pd.read_csv('new_matches.csv')
results = pipeline.incremental_train_with_new_data(new_data, save_model=True)
```

### Demo Model Persistence

```bash
python run_model_persistence_demo.py
```

### Model Management
```python
from ml.ml_pipeline import MLPipeline

# Train and save model
pipeline = MLPipeline()
results = pipeline.run_full_pipeline(save_model=True)

# Load existing model
pipeline.load_existing_model()

# Make predictions
probabilities = pipeline.predict_with_saved_model(new_data)
```

### Model Statistics
```bash
# View model performance statistics
python view_model_stats.py
```

This shows:
- **Performance metrics**: Accuracy, ROC AUC, cross-validation scores
- **Model details**: Version, training date, feature importance
- **Performance trends**: How the model improves over time
- **Data summary**: Matches and players used for training

### Single Match Prediction
```bash
# Make a single prediction with manual input
python single_prediction.py
```

This allows you to:
- **Input all match parameters** manually
- **Test different scenarios** and see predictions
- **Get detailed analysis** of what factors contribute to the prediction
- **Understand model confidence** and performance factors

### API-Style Prediction (Recommended)
```bash
# Configure parameters in code and get predictions
python single_prediction_api.py
```

This allows you to:
- **Edit parameters directly in the code** (like an API body)
- **Quickly test different scenarios** by changing values
- **No console input required** - just modify the `match_body` dictionary
- **Perfect for rapid experimentation** and testing

## 🔧 Configuration

All settings are centralized in `