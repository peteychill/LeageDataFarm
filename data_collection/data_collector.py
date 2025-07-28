"""
Main data collector for League of Legends data.
Orchestrates the entire data collection process.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from config import SUMMONER_NAMES_FILE, LEAGUE_MATCHES_CSV, DATA_DIR
from data_collection.riot_api import RiotAPIClient
from data_collection.data_processor import MatchDataProcessor

logger = setup_logger(__name__)

class DataCollector:
    """Main class for collecting League of Legends data."""
    
    def __init__(self):
        """Initialize the data collector."""
        self.api_client = RiotAPIClient()
        self.processor = MatchDataProcessor()
        
        # Ensure data directory exists
        DATA_DIR.mkdir(exist_ok=True)
        
        logger.info("Data collector initialized")
    
    def load_summoner_names(self) -> List[Dict[str, str]]:
        """
        Load summoner names and tags from the configuration file.
        
        Returns:
            List of summoner dictionaries with 'sName' and 'tag' keys
        """
        try:
            if not SUMMONER_NAMES_FILE.exists():
                raise FileNotFoundError(f"Summoner names file not found at {SUMMONER_NAMES_FILE}")
            
            summoners = []
            with open(SUMMONER_NAMES_FILE, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(':')
                    if len(parts) != 2:
                        logger.warning(f"Invalid format in line {line_num}: {line}")
                        continue
                    
                    summoner = {
                        "sName": parts[0].strip(),
                        "tag": parts[1].strip()
                    }
                    summoners.append(summoner)
            
            logger.info(f"Loaded {len(summoners)} summoner names")
            return summoners
            
        except Exception as e:
            logger.error(f"Error loading summoner names: {e}")
            raise
    
    def collect_player_data(self, summoners: List[Dict[str, str]], start_time: int = None, end_time: int = None) -> Dict[str, Any]:
        """
        Collect match data for all summoners.
        
        Args:
            summoners: List of summoner dictionaries
            start_time: Epoch timestamp in seconds (optional)
            end_time: Epoch timestamp in seconds (optional)
            
        Returns:
            Dictionary containing player data with matches
        """
        summoner_data = {}
        
        for summoner in summoners:
            try:
                logger.info(f"Processing summoner: {summoner['sName']}#{summoner['tag']}")
                
                # Get PUUID
                puuid = self.api_client.get_puuid(summoner['sName'], summoner['tag'])
                if not puuid:
                    logger.error(f"Failed to get PUUID for {summoner['sName']}")
                    continue
                
                # Get match IDs with timestamp filtering
                match_ids = self.api_client.get_match_ids(puuid, start_time=start_time, end_time=end_time)
                if not match_ids:
                    logger.warning(f"No matches found for {summoner['sName']}")
                    continue
                
                # Get match details
                match_details = {}
                for match_id in match_ids:
                    match_data = self.api_client.get_match_details(match_id)
                    if match_data:
                        player_data = self.processor.extract_player_data(match_data, puuid)
                        if player_data:
                            match_details[match_id] = player_data
                
                # Store player data
                player_data = {
                    "sName": summoner['sName'],
                    "tag": summoner['tag'],
                    "puuid": puuid,
                    "lastMatches": match_details
                }
                summoner_data[summoner['sName']] = player_data
                
                logger.info(f"Collected {len(match_details)} matches for {summoner['sName']}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {summoner['sName']}: {e}")
                continue
        
        return summoner_data
    
    def update_csv(self, use_timestamp_filtering: bool = True) -> pd.DataFrame:
        """
        Update the CSV file with new data using timestamp filtering.
        
        Args:
            use_timestamp_filtering: Whether to use timestamp filtering to avoid duplicates
            
        Returns:
            Updated DataFrame
        """
        try:
            logger.info("Starting data collection process")
            
            # Load summoner names
            summoners = self.load_summoner_names()
            
            # Calculate time range for API requests
            start_time = None
            end_time = None
            
            if use_timestamp_filtering:
                # Get latest timestamp from existing data
                latest_timestamp = self.processor.get_latest_timestamp(str(LEAGUE_MATCHES_CSV))
                start_time, end_time = self.processor.calculate_time_range(latest_timestamp)
                
                if latest_timestamp is not None:
                    logger.info(f"Using timestamp filtering to avoid duplicates. Latest timestamp: {latest_timestamp}")
                else:
                    logger.info("No existing data found, will collect default time range")
            else:
                logger.info("Timestamp filtering disabled, collecting all available matches")
            
            # Collect player data with timestamp filtering
            players_data = self.collect_player_data(summoners, start_time=start_time, end_time=end_time)
            
            if not players_data:
                logger.warning("No player data collected")
                return pd.DataFrame()
            
            # Create dataset
            new_df = self.processor.create_match_dataset(players_data)
            
            if new_df.empty:
                logger.warning("No match data to save")
                return pd.DataFrame()
            
            # Merge with existing data
            df = self.processor.merge_with_existing_data(new_df, str(LEAGUE_MATCHES_CSV))
            
            # Save to CSV
            df.to_csv(LEAGUE_MATCHES_CSV, index=False)
            logger.info(f"Successfully saved data to {LEAGUE_MATCHES_CSV}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error updating CSV: {e}")
            raise

def main():
    """Main function to run the data collection process."""
    try:
        collector = DataCollector()
        df = collector.update_csv(use_timestamp_filtering=True)
        
        if not df.empty:
            print(f"Data collection completed successfully!")
            print(f"Total matches: {len(df)}")
            print(f"Unique players: {df['player_name'].nunique()}")
            if 'match_timestamp' in df.columns:
                from datetime import datetime
                # Handle NaN values in match_timestamp
                valid_timestamps = df['match_timestamp'].dropna()
                if not valid_timestamps.empty:
                    latest_time = datetime.fromtimestamp(valid_timestamps.max())
                    earliest_time = datetime.fromtimestamp(valid_timestamps.min())
                    print(f"Date range: {earliest_time} to {latest_time}")
                else:
                    print("No valid timestamps found in data")
            else:
                print(f"Date range: {df['gameVersion'].min()} to {df['gameVersion'].max()}")
        else:
            print("No data was collected")
            
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        raise

if __name__ == "__main__":
    main() 