"""
Data processor for League of Legends match data.
Handles extraction, transformation, and processing of match data.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from config import USE_TIMESTAMP_FILTERING, DEFAULT_DAYS_BACK, TIMESTAMP_BUFFER_HOURS

logger = setup_logger(__name__)

class MatchDataProcessor:
    """Processes and transforms League of Legends match data."""
    
    @staticmethod
    def extract_player_data(match_data: Dict[str, Any], player_puuid: str) -> Optional[Dict[str, Any]]:
        """
        Extract player-specific data from match data.
        
        Args:
            match_data: Raw match data from Riot API
            player_puuid: Player's PUUID to extract data for
            
        Returns:
            Processed player data dictionary or None if player not found
        """
        try:
            info = match_data.get("info", {})
            participants = info.get("participants", [])
            
            # Find the participant for the specified puuid
            player_data = next((p for p in participants if p["puuid"] == player_puuid), None)
            if not player_data:
                logger.warning(f"Player PUUID {player_puuid} not found in match data")
                return None
            
            challenges = player_data.get("challenges", {})
            
            # Convert game duration to formatted string
            duration_seconds = info.get("gameDuration", 0)
            formatted_duration = MatchDataProcessor._format_duration(duration_seconds)
            
            # Extract items
            items = [player_data.get(f"item{i}") for i in range(7)]
            
            # Build result dictionary
            result = {
                "playerPuid": player_puuid,
                "match_id": match_data.get("metadata", {}).get("matchId"),
                "win": player_data.get("win"),
                "gameDuration": formatted_duration,
                "gameVersion": info.get("gameVersion"),
                "championName": player_data.get("championName"),
                "role": player_data.get("teamPosition"),
                "kills": player_data.get("kills", 0),
                "deaths": player_data.get("deaths", 0),
                "assists": player_data.get("assists", 0),
                "totalMinionsKilled": player_data.get("totalMinionsKilled", 0),
                "goldEarned": player_data.get("goldEarned", 0),
                "totalDamageDealtToChampions": player_data.get("totalDamageDealtToChampions", 0),
                "damageDealtToBuildings": player_data.get("damageDealtToBuildings", 0),
                "damageDealtToObjectives": player_data.get("damageDealtToObjectives", 0),
                "controlWardsPlaced": challenges.get("controlWardsPlaced", 0),
                "damageSelfMitigated": player_data.get("damageSelfMitigated", 0),
                "totalDamageTaken": player_data.get("totalDamageTaken", 0),
                "visionScore": player_data.get("visionScore", 0),
                "items": items,
                "maxCsAdvantageOnLaneOpponent": challenges.get("maxCsAdvantageOnLaneOpponent", 0),
                "maxLevelLeadLaneOpponent": challenges.get("maxLevelLeadLaneOpponent", 0),
                "visionScoreAdvantageLaneOpponent": challenges.get("visionScoreAdvantageLaneOpponent", 0),
                "acesBefore15Minutes": challenges.get("acesBefore15Minutes", 0),
                "firstTurretKilled": challenges.get("firstTurretKilled", 0),
                "goldPerMinute": challenges.get("goldPerMinute", 0),
                "killParticipation": challenges.get("killParticipation", 0),
                "maxKillDeficit": challenges.get("maxKillDeficit", 0),
                "quickFirstTurret": challenges.get("quickFirstTurret", 0),
                "soloKills": challenges.get("soloKills", 0),
                "skillshotsDodged": challenges.get("skillshotsDodged", 0),
                "skillshotsHit": challenges.get("skillshotsHit", 0),
                "teamDamagePercentage": challenges.get("teamDamagePercentage", 0),
                "visionScorePerMinute": challenges.get("visionScorePerMinute", 0),
                "damageTakenOnTeamPercentage": challenges.get("damageTakenOnTeamPercentage", 0),
                "quickSoloKills": challenges.get("quickSoloKills", 0),
                "controlWardTimeCoverageInRiverOrEnemyHalf": challenges.get("controlWardTimeCoverageInRiverOrEnemyHalf", 0),
                "match_timestamp": info.get("gameCreation", 0) if info.get("gameCreation") else 0,  # Handle missing gameCreation
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting player data: {e}")
            return None
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def create_match_dataset(players_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Create a pandas DataFrame from player match data.
        
        Args:
            players_data: Dictionary containing player data with matches
            
        Returns:
            DataFrame with all match data
        """
        matches_list = []
        
        for player_name, player_info in players_data.items():
            if not player_info.get('lastMatches'):
                logger.warning(f"No matches found for player {player_name}")
                continue
                
            for match_id, match_details in player_info['lastMatches'].items():
                if not match_details:
                    continue
                    
                # Create match data entry
                match_data = {
                    'player_name': player_name,
                    'match_id': match_id
                }
                
                # Copy all details except playerPuid
                details_copy = match_details.copy()
                details_copy.pop('playerPuid', None)
                
                match_data.update(details_copy)
                matches_list.append(match_data)
        
        df = pd.DataFrame(matches_list)
        logger.info(f"Created dataset with {len(df)} matches from {len(players_data)} players")
        return df
    
    @staticmethod
    def merge_with_existing_data(new_df: pd.DataFrame, csv_path: str) -> pd.DataFrame:
        """
        Merge new data with existing CSV file, removing duplicates.
        
        Args:
            new_df: New data DataFrame
            csv_path: Path to existing CSV file
            
        Returns:
            Merged DataFrame
        """
        try:
            if pd.io.common.file_exists(csv_path):
                existing_df = pd.read_csv(csv_path)
                logger.info(f"Found existing data with {len(existing_df)} records")
                
                # Concatenate existing and new data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # Drop duplicates based on unique identifiers
                df = combined_df.drop_duplicates(
                    subset=['match_id', 'player_name', 'championName', 'gameVersion']
                )
                
                logger.info(f"Merged data: {len(existing_df)} existing + {len(new_df)} new = {len(df)} total")
            else:
                df = new_df
                logger.info(f"No existing data found, using {len(df)} new records")
                
            return df
            
        except Exception as e:
            logger.error(f"Error merging data: {e}")
            return new_df
    
    @staticmethod
    def get_latest_timestamp(csv_path: str) -> Optional[int]:
        """
        Get the latest match timestamp from existing CSV data.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Latest timestamp in seconds, or None if no data exists
        """
        try:
            if not pd.io.common.file_exists(csv_path):
                logger.info("No existing CSV file found")
                return None
            
            df = pd.read_csv(csv_path)
            if df.empty or 'match_timestamp' not in df.columns:
                logger.info("No timestamp data found in CSV")
                return None
            
            # Filter out invalid timestamps (NaN, 0, negative values)
            valid_timestamps = df['match_timestamp'].dropna()
            valid_timestamps = valid_timestamps[valid_timestamps > 0]
            
            if valid_timestamps.empty:
                logger.info("No valid timestamps found in CSV")
                return None
            
            latest_timestamp = int(valid_timestamps.max())
            logger.info(f"Latest timestamp found: {latest_timestamp}")
            return latest_timestamp
            
        except Exception as e:
            logger.error(f"Error getting latest timestamp: {e}")
            return None
    
    @staticmethod
    def calculate_time_range(latest_timestamp: Optional[int] = None) -> tuple[int, int]:
        """
        Calculate start and end time for API requests.
        
        Args:
            latest_timestamp: Latest timestamp from existing data
            
        Returns:
            Tuple of (start_time, end_time) in seconds
        """
        import time
        from datetime import datetime, timedelta
        
        # Current time as end time
        end_time = int(time.time())
        
        if latest_timestamp is not None and latest_timestamp > 0 and USE_TIMESTAMP_FILTERING:
            # Use latest timestamp + buffer as start time
            start_time = latest_timestamp + (TIMESTAMP_BUFFER_HOURS * 3600)  # Add buffer hours
            logger.info(f"Using timestamp filtering: start_time={start_time}, end_time={end_time}")
        else:
            # Use default days back if no existing data or invalid timestamp
            start_time = int((datetime.now() - timedelta(days=DEFAULT_DAYS_BACK)).timestamp())
            logger.info(f"Using default time range: start_time={start_time}, end_time={end_time}")
        
        return start_time, end_time 