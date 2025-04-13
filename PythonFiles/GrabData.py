#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!pip install python-dotenv requests


# In[2]:


import os
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv('../dev.env')  # Simplified to just use the file name since it's in the same directory

# Retrieve the API key from the environment
api_key = os.getenv('RIOT_API_KEY')

# Check if the API key was loaded
if not api_key:
    raise ValueError("RIOT_API_KEY not found in the environment file.")

session = requests.Session()
session.headers.update({"X-Riot-Token": api_key})

riotbaseUrl = "https://americas.api.riotgames.com/"


# In[76]:


def getPid(summonerId, tag):

# Define the URL
    url = f"{riotbaseUrl}riot/account/v1/accounts/by-riot-id/{summonerId}/{tag}"

    # Make the GET request
    response = session.get(url)

    if response.status_code == 200:
        data = response.json()
        puuid = data.get("puuid")
        return puuid
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


# In[90]:


def getMatches(puid):

    #Defaults to 20. Valid values: 0 to 100. Number of match ids to return.
    count = 20
    url = f"{riotbaseUrl}/lol/match/v5/matches/by-puuid/{puid}/ids?count={count}"

    # Make the GET request
    response = session.get(url)

    if response.status_code == 200:
        matchArray = response.json()
        return matchArray
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


# In[93]:


def extractPlayerDataFromMatch(matchData, player_puuid):

    info = matchData.get("info", {})
    participants = info.get("participants", [])

    # Find the participant for the specified puuid
    player_data = next((p for p in participants if p["puuid"] == player_puuid), None)
    if not player_data:
        raise ValueError("Player PUUID not found in match data.")

    # Extract the useful fields
    result = {
        "ranked": info.get("queueId") in [420, 440],
        "win": player_data.get("win"),
        "gameDuration": info.get("gameDuration"),
        "gameMode": info.get("gameMode"),
        "queueId": info.get("queueId"),
        "gameVersion": info.get("gameVersion"),
        "championName": player_data.get("championName"),
        "role": player_data.get("teamPosition"),
        "kills": player_data.get("kills"),
        "deaths": player_data.get("deaths"),
        "assists": player_data.get("assists"),
        "totalMinionsKilled": player_data.get("totalMinionsKilled"),
        "neutralMinionsKilled": player_data.get("neutralMinionsKilled"),
        "goldEarned": player_data.get("goldEarned"),
        "damageDealtToChampions": player_data.get("damageDealtToChampions"),
        "damageDealtToBuildings": player_data.get("damageDealtToBuildings"),
        "damageDealtToObjectives": player_data.get("damageDealtToObjectives"),
        "controlWardTimeCoverageInRiverOrEnemyHalf": player_data.get("controlWardTimeCoverageInRiverOrEnemyHalf"),
        "controlWardsPlaced": player_data.get("controlWardsPlaced"),
        "totalDamageDealtToChampions": player_data.get("totalDamageDealtToChampions"),
        "damageSelfMitigated": player_data.get("damageSelfMitigated"),
        "teamDamagePercentage": player_data.get("teamDamagePercentage"),
        "damageTakenOnTeamPercentage": player_data.get("damageTakenOnTeamPercentage"),
        "damageTaken": player_data.get("damageTaken"),
        "visionScore": player_data.get("visionScore"),
        "items": [
            player_data.get(f"item{i}") for i in range(7)
        ],
        "summonerSpells": [
            player_data.get("summoner1Id"),
            player_data.get("summoner2Id")
        ],
        "challenges": player_data.get("challenges", {})  # optional detailed stats
    }



    return result


# In[52]:


def getMatchDetails(matchId, puuid):

    url = f"{riotbaseUrl}/lol/match/v5/matches/{matchId}"

    response = session.get(url)

    if response.status_code == 200:
        matchDetails = response.json()
        playerDetailsForMatch = extractPlayerDataFromMatch(matchDetails, puuid)
        return playerDetailsForMatch
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


# In[83]:


def getPlayerData():
    with open('summonerNames.txt', 'r') as file:
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
                details = getMatchDetails(match, puuid)  # Get the match details
                if details and details.get("ranked", False):  # Only add if we got valid details
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


# In[ ]:


#allPlayersData = getPlayerData()
#print(allPlayersData)

