import os
import pandas as pd
import json
from datetime import datetime, timedelta
import sys

def round_down_to_even_minutes(timestamp):
    """Round down timestamp minutes to nearest even number and format consistently"""
    rounded_minute = timestamp.minute - (timestamp.minute % 2)
    rounded_time = timestamp.replace(minute=rounded_minute, second=0, microsecond=0)
    return rounded_time.strftime("%Y-%m-%dT%H:%M:00")

def load_app_data(app_data_path):
    """Load and process app emotion data"""
    app_data = pd.read_csv(app_data_path)
    print("Successfully loaded app data")
    # Remove Z suffix from timestamp column
    app_data['timestamp'] = app_data['timestamp'].str.replace('Z', '')
    print("\nApp data shape:", app_data.shape)
    return app_data

def load_manual_data(manual_data_path):
    """Load and process manual emotion data"""
    try:
        with open(manual_data_path, 'r') as f:
            manual_data = json.load(f)
        manual_df = pd.DataFrame(manual_data)
        print("Successfully loaded manual emotion data")
        manual_df['timestamp'] = manual_df['timestamp'].str.replace('Z', '')
        
        # Convert timestamp to datetime and round to even minutes
        manual_df['timestamp'] = pd.to_datetime(manual_df['timestamp'])
        manual_df['timestamp'] = manual_df['timestamp'].apply(round_down_to_even_minutes)
        
        print("\nManual data shape:", manual_df.shape)
        return manual_df
    except Exception as e:
        print(f"Error loading manual data: {e}")
        return pd.DataFrame()

def load_health_data(health_data_path):
    """Load and process health data"""
    health_data = pd.read_csv(health_data_path)
    print("Successfully loaded health data")
    
    # Drop timestamp column and rename local_time to timestamp
    health_data = health_data.drop(columns=['timestamp'])
    # health_data = health_data.rename(columns={'timestamp': 'GMT_timestamp'})
    health_data = health_data.rename(columns={'local_time': 'timestamp'})
    
    print("\nHealth data shape:", health_data.shape)
    return health_data

def combine_emotion_data(app_data, manual_df):
    """Combine app and manual emotion data"""
    # Concatenate app_data and manual_df
    combined_df = pd.concat([app_data, manual_df], ignore_index=True)
    
    # Sort by timestamp
    combined_df = combined_df.sort_values('timestamp')
    
    # Reset index after sorting
    combined_df = combined_df.reset_index(drop=True)
    
    print("\nCombined data shape:", combined_df.shape)
    return combined_df

def merge_datasets(health_data, non_missing_df):
    """Merge health data with emotion data"""
    # Merge on timestamps
    merged_data = pd.merge(health_data, non_missing_df, on='timestamp', how='left')
    print("\nMerged data shape:", merged_data.shape)
    return merged_data

def main():
    # Get the root directory path
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Add root directory to Python path
    sys.path.append(ROOT_DIR)
    
    # Set working directory to root
    os.chdir(ROOT_DIR)
    
    # Define file paths
    DATA_DIR = "data"
    app_data_path = os.path.join(ROOT_DIR, 'my-va-app', DATA_DIR, 'emotion_data.csv')
    manual_data_path = os.path.join(DATA_DIR, 'raw/emotion_data.json')
    health_data_path = os.path.join(DATA_DIR, 'processed/garmin_data.csv')
    
    # Load and process data
    app_data = load_app_data(app_data_path)
    manual_df = load_manual_data(manual_data_path)
    health_data = load_health_data(health_data_path)
    
    # make sure all timestamps are in format YYYY-MM-DD HH:MM:SS
    app_data['timestamp'] = pd.to_datetime(app_data['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    manual_df['timestamp'] = pd.to_datetime(manual_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    health_data['timestamp'] = pd.to_datetime(health_data['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Combine emotion data
    combined_df = combine_emotion_data(app_data, manual_df)
    
    # Create non-missing dataframe
    non_missing_df = combined_df[combined_df['valence'].notna() & 
                               combined_df['arousal'].notna() & 
                               combined_df['emotion'].notna()]
    non_missing_df = non_missing_df.drop(columns=['hue', 'saturation', 'brightness'])
    
    # Merge datasets
    merged_data = merge_datasets(health_data, non_missing_df)
    
    # Create labelled data
    labelled_data = pd.merge(non_missing_df, health_data, on='timestamp', how='left')
    
    # Save results
    combined_df.to_csv(os.path.join(DATA_DIR, 'merged/combined_emotion_data.csv'), index=False)
    merged_data.to_csv(os.path.join(DATA_DIR, 'merged/merged_data.csv'), index=False)
    labelled_data.to_csv(os.path.join(DATA_DIR, 'merged/labelled_data.csv'), index=False)
    
    print("\n✅ All data saved successfully!")

if __name__ == "__main__":
    main() 