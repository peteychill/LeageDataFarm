"""
Configuration file for League Data Farm project.
Centralizes all settings, API configurations, and parameters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../dev.env')

# API Configuration
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
RIOT_BASE_URL = "https://americas.api.riotgames.com/"

# Data Collection Settings
MATCH_COUNT = 5  # Number of matches to fetch per player
REQUEST_TIMEOUT = 30  # API request timeout in seconds
RATE_LIMIT_DELAY = 120  # Delay when rate limited (seconds)

# Timestamp-based collection settings
USE_TIMESTAMP_FILTERING = True  # Enable timestamp-based filtering
DEFAULT_DAYS_BACK = 60  # Default days to look back if no existing data
TIMESTAMP_BUFFER_HOURS = 1  # Buffer hours to avoid missing matches due to timezone differences

# File Paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'Data'
SUMMONER_NAMES_FILE = DATA_DIR / 'summonerNames.txt'
LEAGUE_MATCHES_CSV = DATA_DIR / 'league_matches.csv'

# Model Persistence Settings
MODELS_DIR = PROJECT_ROOT / 'models'
MODEL_FILE = MODELS_DIR / 'league_win_predictor.pkl'
SCALER_FILE = MODELS_DIR / 'feature_scaler.pkl'
ENCODERS_FILE = MODELS_DIR / 'label_encoders.pkl'
FEATURE_COLUMNS_FILE = MODELS_DIR / 'feature_columns.json'
MODEL_STATS_FILE = MODELS_DIR / 'model_statistics.json'  # Model performance tracking

# Machine Learning Settings
ML_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'class_weight': 'balanced'
}

# Feature Engineering Settings
FEATURE_COLUMNS = [
    'championName', 'role',
    'kda', 'damage_per_min', 'vision_per_min',
    'goldPerMinute', 'killParticipation',
    'maxCsAdvantageOnLaneOpponent', 'maxLevelLeadLaneOpponent',
    'visionScoreAdvantageLaneOpponent',
    'skillshotsHit', 'skillshotsDodged',
    'teamDamagePercentage', 'damageTakenOnTeamPercentage',
    'controlWardTimeCoverageInRiverOrEnemyHalf'
]

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' 