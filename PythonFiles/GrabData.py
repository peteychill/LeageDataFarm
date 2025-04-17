#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!pip install python-dotenv requests


# In[2]:


import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import time
import pandas as pd

load_dotenv('../dev.env')  # Simplified to just use the file name since it's in the same directory

# Retrieve the API key from the environment
api_key = os.getenv('RIOT_API_KEY')

# Check if the API key was loaded
if not api_key:
    raise ValueError("RIOT_API_KEY not found in the environment file.")

session = requests.Session()
session.headers.update({"X-Riot-Token": api_key})

riotbaseUrl = "https://americas.api.riotgames.com/"


# In[3]:


def getPid(summonerId, tag):

# Define the URL
    url = f"{riotbaseUrl}riot/account/v1/accounts/by-riot-id/{summonerId}/{tag}"

    # Make the GET request
    response = session.get(url)

    if response.status_code == 200:
        data = response.json()
        puuid = data.get("puuid")
        return puuid
    if response.status_code == 429:
        time.sleep(120)
        return getPid(summonerId, tag)
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


# In[4]:


def getMatches(puid):

    #Defaults to 20. Valid values: 0 to 100. Number of match ids to return.
    count = 5
    url = f"{riotbaseUrl}/lol/match/v5/matches/by-puuid/{puid}/ids?count={count}&type=ranked"

    # Make the GET request
    response = session.get(url)

    if response.status_code == 200:
        matchArray = response.json()
        return matchArray
    if response.status_code == 429:
        time.sleep(120)
        return getMatches(puid)
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


# In[5]:


def extractPlayerDataFromMatch(matchData, player_puuid):

    info = matchData.get("info", {})
    participants = info.get("participants", [])

    # Find the participant for the specified puuid
    player_data = next((p for p in participants if p["puuid"] == player_puuid), None)
    if not player_data:
        raise ValueError("Player PUUID not found in match data.")

    challenges = player_data.get("challenges", {})

    # Convert game duration to hours:minutes:seconds
    duration_seconds = info.get("gameDuration", 0)
    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60
    seconds = duration_seconds % 60
    formatted_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Extract the useful fields
    result = {
        "playerPuid": player_puuid,
        "win": player_data.get("win"),
        "gameDuration": formatted_duration,
        "gameVersion": info.get("gameVersion"),
        "championName": player_data.get("championName"),
        "role": player_data.get("teamPosition"),
        "kills": player_data.get("kills"),
        "deaths": player_data.get("deaths"),
        "assists": player_data.get("assists"),
        "totalMinionsKilled": player_data.get("totalMinionsKilled"),
        "goldEarned": player_data.get("goldEarned"),
        "totalDamageDealtToChampions": player_data.get("totalDamageDealtToChampions"),
        "damageDealtToBuildings": player_data.get("damageDealtToBuildings"),
        "damageDealtToObjectives": player_data.get("damageDealtToObjectives"),
        "controlWardsPlaced": challenges.get("controlWardsPlaced"),
        "totalDamageDealtToChampions": player_data.get("totalDamageDealtToChampions"),
        "damageSelfMitigated": player_data.get("damageSelfMitigated"),
        "totalDamageTaken": player_data.get("totalDamageTaken"),
        "visionScore": player_data.get("visionScore"),
        "items": [
            player_data.get(f"item{i}") for i in range(7)
        ],
        "maxCsAdvantageOnLaneOpponent": challenges.get("maxCsAdvantageOnLaneOpponent"),
        "maxLevelLeadLaneOpponent": challenges.get("maxLevelLeadLaneOpponent"),
        "visionScoreAdvantageLaneOpponent": challenges.get("visionScoreAdvantageLaneOpponent"),
        "acesBefore15Minutes": challenges.get("acesBefore15Minutes"),
        "firstTurretKilled": challenges.get("firstTurretKilled"),
        "goldPerMinute": challenges.get("goldPerMinute"),
        "killParticipation": challenges.get("killParticipation"),
        "maxKillDeficit": challenges.get("maxKillDeficit"),
        "quickFirstTurret": challenges.get("quickFirstTurret"),
        "soloKills": challenges.get("soloKills"),
        "skillshotsDodged": challenges.get("skillshotsDodged"),
        "skillshotsHit": challenges.get("skillshotsHit"),
        "teamDamagePercentage": challenges.get("teamDamagePercentage"),
        "visionScorePerMinute": challenges.get("visionScorePerMinute"),
        "damageTakenOnTeamPercentage": challenges.get("damageTakenOnTeamPercentage"),
        "quickSoloKills": challenges.get("quickSoloKills"),
        "controlWardTimeCoverageInRiverOrEnemyHalf": challenges.get("controlWardTimeCoverageInRiverOrEnemyHalf", 0),
    }
    return result


# In[6]:


def getMatchDetails(matchId, puuid):

    url = f"{riotbaseUrl}/lol/match/v5/matches/{matchId}"

    response = session.get(url)

    if response.status_code == 200:
        matchDetails = response.json()
        playerDetailsForMatch = extractPlayerDataFromMatch(matchDetails, puuid)
        return playerDetailsForMatch
    if response.status_code == 429:
        time.sleep(120)
        return getMatchDetails(matchId, puuid)
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


# In[7]:


def getPlayerData():
    # Define data directory path
    data_dir = Path('Data')
    file_path = data_dir / 'summonerNames.txt'

    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"Summoner names file not found at {file_path}")

    with open(file_path, 'r') as file:
        # Read each line and create user objects
        summoners = []
        for line in file:
            # Split the line by colon and strip whitespace
            parts = line.strip().split(':')
            if len(parts) == 2:
                user = {
                    "sName": parts[0].strip(),
                    "tag": parts[1].strip()
                }
                summoners.append(user)

    # Initialize the dictionary before the loop
    summoner_data = {}

    for user in summoners:
        puuid = getPid(user['sName'], user['tag'])  # Updated format for API call
        if puuid:  # Only proceed if we got a valid PUUID
            matches = getMatches(puuid)
            matchDetails = {}
            for match in matches:
                details = getMatchDetails(match, puuid)  # Get the match details  # Only add if we got valid details
                matchDetails[match] = details  # Use match ID as key
            # Create a player object with both PUUID and matches
            player_data = {
                "sName": user['sName'],
                "tag": user['tag'],
                "puuid": puuid,
                "lastMatches": matchDetails if matchDetails else []  # Use empty list if no matches found
            }
            summoner_data[user['sName']] = player_data
        else:
            print(f"Failed to get data for {user['sName']}")

    return summoner_data


# In[8]:


def create_match_dataset(players_data):
    # Initialize a list to store all match data
    matches_list = []

    # Iterate through each player
    for player_name, player_info in players_data.items():
        # Get the matches for this player
        for match_id, match_details in player_info['lastMatches'].items():
            # Create a new dictionary starting with player name and match_id
            match_data = {
                'player_name': player_name,
                'match_id': match_id
            }

            # Copy all other details except playerPuid
            details_copy = match_details.copy()
            details_copy.pop('playerPuid', None)  # Remove playerPuid if it exists

            # Update match_data with remaining details
            match_data.update(details_copy)

            # Append to matches list
            matches_list.append(match_data)

    # Convert to DataFrame
    df = pd.DataFrame(matches_list)

    return df


# In[9]:


def get_project_root():
    try:
        current_path = Path().absolute()

        # Traverse up until we find the LeagueDataFarm directory
        while current_path.name != 'LeagueDataFarm' and current_path != current_path.parent:
            current_path = current_path.parent

        # If we're now inside LeagueDataFarm, return the path
        if current_path.name == 'LeagueDataFarm':
            return current_path

        # If not found
        print("Warning: LeagueDataFarm folder not found.")
        return None

    except Exception as e:
        print(f"Error while locating LeagueDataFarm folder: {e}")
        return None


# In[10]:


# Create the Data directory if it doesn't exist
def updateCsv():
    project_root = get_project_root()
    data_dir = project_root / 'Data'

    # Ensure the directory exists
    try:
        data_dir.mkdir(exist_ok=True)
    except Exception as e:
        print(f"Error creating Data directory: {e}")
        raise

    csv_path = data_dir / 'league_matches.csv'

    # Create and display the dataset
    playerData = getPlayerData()
    new_df = create_match_dataset(playerData)

    try:
        # If CSV exists, merge with new data, otherwise create new CSV
        if csv_path.exists():
            # Read existing data
            existing_df = pd.read_csv(csv_path)

            # Concatenate existing and new data
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)

            # Drop duplicates based on specific columns that uniquely identify a match
            df = combined_df.drop_duplicates(subset=['match_id', 'player_name', 'championName', 'gameVersion'])

        else:
            df = new_df

        # Save to CSV
        df.to_csv(csv_path, index=False)
        print(f"Successfully saved data to {csv_path}")

    except Exception as e:
        print(f"Error processing CSV data: {e}")
        raise


# In[ ]:


#updateCsv()

