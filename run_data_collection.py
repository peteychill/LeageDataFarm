#!/usr/bin/env python3
"""
Simple script to run data collection.
Usage: python run_data_collection.py [--no-timestamp-filtering]
"""

import argparse
from data_collection.data_collector import DataCollector

def main():
    """Main function with command line argument support."""
    parser = argparse.ArgumentParser(description='Collect League of Legends match data')
    parser.add_argument('--no-timestamp-filtering', 
                       action='store_true',
                       help='Disable timestamp filtering (collect all available matches)')
    
    args = parser.parse_args()
    
    try:
        collector = DataCollector()
        use_timestamp_filtering = not args.no_timestamp_filtering
        
        print(f"Timestamp filtering: {'Enabled' if use_timestamp_filtering else 'Disabled'}")
        
        df = collector.update_csv(use_timestamp_filtering=use_timestamp_filtering)
        
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
        print(f"Data collection failed: {e}")
        raise

if __name__ == "__main__":
    main() 