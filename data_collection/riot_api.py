"""
Riot API client for League of Legends data collection.
Handles API requests with proper error handling and rate limiting.
"""

import requests
import time
from typing import Optional, Dict, List, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from config import (
    RIOT_API_KEY, RIOT_BASE_URL, REQUEST_TIMEOUT, 
    RATE_LIMIT_DELAY, MATCH_COUNT
)

logger = setup_logger(__name__)

class RiotAPIClient:
    """Client for interacting with Riot Games API."""
    
    def __init__(self):
        """Initialize the API client with authentication."""
        if not RIOT_API_KEY:
            raise ValueError("RIOT_API_KEY not found in environment variables")
        
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": RIOT_API_KEY})
        self.session.timeout = REQUEST_TIMEOUT
        
        logger.info("Riot API client initialized")
    
    def _make_request(self, url: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Make an API request with retry logic and error handling.
        
        Args:
            url: API endpoint URL
            retries: Number of retry attempts
            
        Returns:
            JSON response data or None if failed
        """
        for attempt in range(retries):
            try:
                response = self.session.get(url)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    logger.warning(f"Rate limited, waiting {RATE_LIMIT_DELAY} seconds...")
                    time.sleep(RATE_LIMIT_DELAY)
                    continue
                elif response.status_code == 404:
                    logger.error(f"Resource not found: {url}")
                    return None
                else:
                    logger.error(f"API request failed: {response.status_code} - {response.text}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    def get_puuid(self, summoner_id: str, tag: str) -> Optional[str]:
        """
        Get PUUID for a summoner by their Riot ID.
        
        Args:
            summoner_id: Summoner name
            tag: Summoner tag
            
        Returns:
            PUUID string or None if not found
        """
        url = f"{RIOT_BASE_URL}riot/account/v1/accounts/by-riot-id/{summoner_id}/{tag}"
        logger.info(f"Fetching PUUID for {summoner_id}#{tag}")
        
        data = self._make_request(url)
        if data:
            puuid = data.get("puuid")
            logger.info(f"Successfully retrieved PUUID for {summoner_id}")
            return puuid
        else:
            logger.error(f"Failed to get PUUID for {summoner_id}#{tag}")
            return None
    
    def get_match_ids(self, puuid: str, count: int = None, start_time: int = None, end_time: int = None) -> Optional[List[str]]:
        """
        Get recent match IDs for a player.
        
        Args:
            puuid: Player's PUUID
            count: Number of matches to fetch (defaults to config value)
            start_time: Epoch timestamp in seconds (optional)
            end_time: Epoch timestamp in seconds (optional)
            
        Returns:
            List of match IDs or None if failed
        """
        count = count or MATCH_COUNT
        
        # Build URL with optional timestamp parameters
        url = f"{RIOT_BASE_URL}lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}&type=ranked"
        
        if start_time is not None:
            url += f"&startTime={start_time}"
        if end_time is not None:
            url += f"&endTime={end_time}"
        
        logger.info(f"Fetching {count} match IDs for player (start_time: {start_time}, end_time: {end_time})")
        
        data = self._make_request(url)
        if data:
            logger.info(f"Successfully retrieved {len(data)} match IDs")
            return data
        else:
            logger.error("Failed to get match IDs")
            return None
    
    def get_match_details(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed match information.
        
        Args:
            match_id: Match ID to fetch
            
        Returns:
            Match details dictionary or None if failed
        """
        url = f"{RIOT_BASE_URL}lol/match/v5/matches/{match_id}"
        logger.debug(f"Fetching match details for {match_id}")
        
        return self._make_request(url) 