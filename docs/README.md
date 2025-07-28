# League Data Farm - Documentation

Welcome to the League Data Farm documentation! This folder contains comprehensive guides and documentation for the project.

## 📚 Documentation Index

### 🚀 Getting Started
- **[README.md](../README.md)** - Main project overview and quick start guide

### 📖 Guides
- **[TIMESTAMP_FILTERING_GUIDE.md](./TIMESTAMP_FILTERING_GUIDE.md)** - Complete guide to timestamp-based data collection
- **[MODEL_PERSISTENCE_GUIDE.md](./MODEL_PERSISTENCE_GUIDE.md)** - Guide to saving, loading, and incrementally training models
- **[OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)** - Summary of project optimization and improvements

## 🎯 Quick Navigation

### For Data Collection
- **Timestamp Filtering**: [TIMESTAMP_FILTERING_GUIDE.md](./TIMESTAMP_FILTERING_GUIDE.md)
  - Learn how to avoid duplicate data collection
  - Configure time-based filtering
  - Optimize API usage

### For Machine Learning
- **Model Persistence**: [MODEL_PERSISTENCE_GUIDE.md](./MODEL_PERSISTENCE_GUIDE.md)
  - Save and load trained models
  - Incremental training with new data
  - Production-ready model management

### For Project Understanding
- **Optimization Summary**: [OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)
  - Learn about the project's evolution
  - Understand the modular architecture
  - Migration guide from old workflow

## 🔧 Usage Examples

### Data Collection with Timestamp Filtering
```bash
# Collect only new matches since last run
python run_data_collection.py

# Collect all available matches (ignores existing data)
python run_data_collection.py --no-timestamp-filtering
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

## 📁 Project Structure

```
LeagueDataFarm/
├── docs/                          # 📚 Documentation
│   ├── README.md                  # This file
│   ├── TIMESTAMP_FILTERING_GUIDE.md
│   ├── MODEL_PERSISTENCE_GUIDE.md
│   └── OPTIMIZATION_SUMMARY.md
├── data_collection/               # Data collection modules
├── ml/                           # Machine learning modules
├── utils/                        # Utility modules
├── Data/                         # Data storage
├── models/                       # Saved models
└── README.md                     # Main project README
```

## 🚀 Next Steps

1. **Start with the main [README.md](../README.md)** for project overview
2. **Read [TIMESTAMP_FILTERING_GUIDE.md](./TIMESTAMP_FILTERING_GUIDE.md)** if you're collecting data
3. **Read [MODEL_PERSISTENCE_GUIDE.md](./MODEL_PERSISTENCE_GUIDE.md)** if you're working with ML models
4. **Read [OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)** to understand the project's architecture

## 📞 Support

If you need help with any specific aspect of the project:

- **Data Collection Issues**: Check [TIMESTAMP_FILTERING_GUIDE.md](./TIMESTAMP_FILTERING_GUIDE.md)
- **Model Training Issues**: Check [MODEL_PERSISTENCE_GUIDE.md](./MODEL_PERSISTENCE_GUIDE.md)
- **General Questions**: Check the main [README.md](../README.md)

---

*Happy coding! 🎮* 