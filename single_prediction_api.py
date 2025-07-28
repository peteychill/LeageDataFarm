#!/usr/bin/env python3
"""
Single Match Prediction API Tool
Allows you to configure match parameters in a body and get predictions.
Usage: python single_prediction_api.py
"""

import pandas as pd
import numpy as np
from ml.ml_pipeline import MLPipeline
from config import LEAGUE_MATCHES_CSV

def get_default_match_body() -> dict:
    """Get the default match body with all parameters."""
    return {
        # Basic match info
        "championName": "Yasuo",
        "role": "MIDDLE",
        
        # Combat statistics
        "kills": 8,
        "deaths": 3,
        "assists": 5,
        
        # Economic statistics
        "totalMinionsKilled": 180,
        "goldEarned": 12000,
        
        # Damage statistics
        "totalDamageDealtToChampions": 25000,
        "damageDealtToBuildings": 5000,
        "damageDealtToObjectives": 3000,
        "damageSelfMitigated": 8000,
        "totalDamageTaken": 15000,
        
        # Vision statistics
        "visionScore": 25,
        "controlWardsPlaced": 2,
        
        # Advanced statistics
        "maxCsAdvantageOnLaneOpponent": 15,
        "maxLevelLeadLaneOpponent": 2,
        "visionScoreAdvantageLaneOpponent": 5,
        
        # Team performance
        "acesBefore15Minutes": 0,
        "firstTurretKilled": 1,
        "goldPerMinute": 450,
        "killParticipation": 0.7,
        "maxKillDeficit": 3,
        "quickFirstTurret": 0,
        "soloKills": 2,
        
        # Skill statistics
        "skillshotsDodged": 15,
        "skillshotsHit": 45,
        "teamDamagePercentage": 0.25,
        "visionScorePerMinute": 0.8,
        "damageTakenOnTeamPercentage": 0.2,
        "quickSoloKills": 1,
        "controlWardTimeCoverageInRiverOrEnemyHalf": 0.3,
        
        # Game duration (HH:MM:SS format)
        "gameDuration": "25:30:00",
        
        # Placeholder for prediction
        "win": False
    }

def display_match_body(match_body: dict) -> None:
    """Display the current match body in a readable format."""
    print("🎮 Current Match Configuration:")
    print("=" * 60)
    
    # Basic info
    print(f"🏆 Champion: {match_body['championName']} ({match_body['role']})")
    print(f"⏱️ Game Duration: {match_body['gameDuration']}")
    print()
    
    # Combat stats
    kda = (match_body['kills'] + match_body['assists']) / max(match_body['deaths'], 1)
    print(f"⚔️ Combat: {match_body['kills']}/{match_body['deaths']}/{match_body['assists']} (KDA: {kda:.2f})")
    
    # Economic stats
    print(f"💰 Economy: {match_body['goldEarned']:,} gold ({match_body['goldPerMinute']:.0f}/min)")
    print(f"🌾 CS: {match_body['totalMinionsKilled']} minions")
    
    # Damage stats
    print(f"💥 Damage: {match_body['totalDamageDealtToChampions']:,} to champs")
    print(f"🛡️ Taken: {match_body['totalDamageTaken']:,} damage")
    
    # Vision stats
    print(f"👁️ Vision: {match_body['visionScore']} score, {match_body['controlWardsPlaced']} control wards")
    
    # Team stats
    print(f"🎯 Team: {match_body['killParticipation']:.1%} kill participation")
    print(f"🏆 Solo: {match_body['soloKills']} solo kills")
    
    print()

def make_prediction(match_body: dict) -> dict:
    """Make a prediction using the provided match body."""
    try:
        # Load the saved model
        pipeline = MLPipeline()
        
        if not pipeline.load_existing_model():
            return {
                "error": "No saved model found. Please train a model first.",
                "success": False
            }
        
        # Convert game duration to seconds for feature engineering
        duration_parts = match_body['gameDuration'].split(':')
        if len(duration_parts) == 3:
            hours, minutes, seconds = map(int, duration_parts)
            match_body['gameDuration_seconds'] = hours * 3600 + minutes * 60 + seconds
        else:
            match_body['gameDuration_seconds'] = 1500  # Default 25 minutes
        
        # Create DataFrame for prediction
        df = pd.DataFrame([match_body])
        
        # Make prediction
        probabilities = pipeline.predict_with_saved_model(df)
        probability = probabilities[0]
        
        # Calculate derived features for analysis
        kda = (match_body['kills'] + match_body['assists']) / max(match_body['deaths'], 1)
        damage_per_min = match_body['totalDamageDealtToChampions'] / max(match_body['gameDuration_seconds'], 1) * 60
        vision_per_min = match_body['visionScore'] / max(match_body['gameDuration_seconds'], 1) * 60
        
        # Determine prediction and confidence
        predicted_win = "WIN" if probability > 0.5 else "LOSS"
        confidence = max(probability, 1 - probability) * 100
        
        # Confidence level
        if confidence >= 80:
            confidence_level = "Very High"
            confidence_emoji = "🟢"
        elif confidence >= 70:
            confidence_level = "High"
            confidence_emoji = "🟢"
        elif confidence >= 60:
            confidence_level = "Medium"
            confidence_emoji = "🟡"
        else:
            confidence_level = "Low"
            confidence_emoji = "🔴"
        
        # Analyze key factors
        factors = []
        if kda > 3.0:
            factors.append("✅ Strong KDA performance")
        elif kda < 1.0:
            factors.append("❌ Poor KDA performance")
        
        if match_body['goldPerMinute'] > 400:
            factors.append("✅ Good gold generation")
        elif match_body['goldPerMinute'] < 250:
            factors.append("❌ Low gold generation")
        
        if match_body['visionScore'] > 25:
            factors.append("✅ Good vision control")
        elif match_body['visionScore'] < 10:
            factors.append("❌ Poor vision control")
        
        if match_body['killParticipation'] > 0.6:
            factors.append("✅ High team participation")
        elif match_body['killParticipation'] < 0.3:
            factors.append("❌ Low team participation")
        
        if damage_per_min > 1000:
            factors.append("✅ High damage output")
        elif damage_per_min < 500:
            factors.append("❌ Low damage output")
        
        return {
            "success": True,
            "prediction": {
                "result": predicted_win,
                "probability": float(probability),
                "confidence_percentage": float(confidence),
                "confidence_level": confidence_level,
                "confidence_emoji": confidence_emoji
            },
            "analysis": {
                "kda": float(kda),
                "damage_per_minute": float(damage_per_min),
                "vision_per_minute": float(vision_per_min),
                "key_factors": factors
            },
            "match_stats": {
                "champion": match_body['championName'],
                "role": match_body['role'],
                "kills": match_body['kills'],
                "deaths": match_body['deaths'],
                "assists": match_body['assists'],
                "gold_earned": match_body['goldEarned'],
                "gold_per_minute": match_body['goldPerMinute'],
                "vision_score": match_body['visionScore'],
                "kill_participation": match_body['killParticipation']
            }
        }
        
    except Exception as e:
        return {
            "error": f"Prediction failed: {str(e)}",
            "success": False
        }

def main():
    """Run the API-style prediction tool."""
    print("🎮 League Data Farm - Single Match Prediction API")
    print("=" * 60)
    print("This tool allows you to configure match parameters and get predictions.")
    print("Edit the match_body below to test different scenarios!")
    print()
    
    # Get the default match body
    match_body = get_default_match_body()
    
    # Display current configuration
    display_match_body(match_body)
    
    print("📝 To modify parameters, edit the match_body in this file and run again.")
    print("Or you can modify the values programmatically in the code.")
    print()
    
    # Make prediction
    print("🔮 Making prediction...")
    result = make_prediction(match_body)
    
    if result["success"]:
        prediction = result["prediction"]
        analysis = result["analysis"]
        stats = result["match_stats"]
        
        print("=" * 60)
        print("🎯 PREDICTION RESULT")
        print("=" * 60)
        
        print(f"🏆 Champion: {stats['champion']} ({stats['role']})")
        print(f"⚔️ KDA: {stats['kills']}/{stats['deaths']}/{stats['assists']} ({analysis['kda']:.2f})")
        print(f"💰 Gold: {stats['gold_earned']:,} ({stats['gold_per_minute']:.1f}/min)")
        print(f"💥 Damage: {match_body['totalDamageDealtToChampions']:,} ({analysis['damage_per_minute']:.1f}/min)")
        print(f"👁️ Vision: {stats['vision_score']} ({analysis['vision_per_minute']:.2f}/min)")
        print()
        
        print(f"🎯 PREDICTION: {prediction['result']}")
        print(f"📊 Win Probability: {prediction['probability']:.1%}")
        print(f"🎲 Confidence: {prediction['confidence_percentage']:.1f}%")
        print(f"{prediction['confidence_emoji']} Confidence Level: {prediction['confidence_level']}")
        
        if analysis['key_factors']:
            print("\n🔍 Key Performance Factors:")
            print("-" * 30)
            for factor in analysis['key_factors']:
                print(f"  {factor}")
        else:
            print("\n📊 Balanced performance across metrics")
            
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("💡 Tips for testing different scenarios:")
    print("• Change champion/role combinations")
    print("• Adjust KDA ratios (high kills/low deaths vs low kills/high deaths)")
    print("• Modify gold generation (high vs low gold per minute)")
    print("• Test vision control (high vs low vision score)")
    print("• Experiment with team participation (high vs low kill participation)")
    print("• Try different damage outputs (carry vs support levels)")

if __name__ == "__main__":
    main() 