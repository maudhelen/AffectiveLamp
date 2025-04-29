import argparse
import json
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import pytz
import subprocess

# Add root directory to Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# Redirect all debug output to stderr
def debug_print(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

debug_print("\n=== Starting Emotion Prediction ===")
debug_print(f"Current working directory: {os.getcwd()}")
debug_print(f"Root directory: {ROOT_DIR}")

# Check if required model files exist
required_files = [
    os.path.join(ROOT_DIR, 'models', 'trained', 'valence_scaler.joblib'),
    os.path.join(ROOT_DIR, 'models', 'trained', 'arousal_scaler.joblib'),
    os.path.join(ROOT_DIR, 'models', 'trained', 'best_valence_model.joblib'),
    os.path.join(ROOT_DIR, 'models', 'trained', 'best_arousal_model.joblib')
]

debug_print("\nChecking for required files:")
for f in required_files:
    debug_print(f"- {f}: {'✅ Found' if os.path.exists(f) else '❌ Missing'}")

missing_files = [f for f in required_files if not os.path.exists(f)]
if missing_files:
    debug_print("\n❌ Error: Missing required model files:")
    for f in missing_files:
        debug_print(f"- {f}")
    debug_print("\nPlease ensure all model files are present in the models/trained/ directory.")
    print(json.dumps({"error": "Missing required model files"}))
    sys.exit(1)

debug_print("✅ All required model files found")

try:
    from data_processing.retrieval.last_x_days import fetch_garmin_health_data
    from data_processing.conversion.json_to_csv import process_garmin_data, create_dataframe
    from data_processing.cleaning.clean_data import handle_missing_values
    from data_processing.cleaning.process_features import add_lag_features, encode_categorical_variables
    debug_print("✅ All required imports loaded successfully")
except ImportError as e:
    debug_print(f"\n❌ Error importing required modules: {str(e)}")
    debug_print(f"Python path: {sys.path}")
    print(json.dumps({"error": f"Error importing required modules: {str(e)}"}))
    sys.exit(1)

def load_garmin_data(garmin_file):
    """Load Garmin health data from JSON file."""
    with open(garmin_file, "r") as f:
        garmin_data = json.load(f)
    debug_print("✅ Loaded Garmin health data")
    return garmin_data

def find_closest_data_point(df, target_dt):
    """Find the closest data point to the target timestamp."""
    # Calculate time differences
    time_diff = abs(df['timestamp'] - target_dt)
    closest_idx = time_diff.idxmin()
    closest_time = df.loc[closest_idx, 'timestamp']
    
    # Check if the closest point is within 2 minutes
    if abs((closest_time - target_dt).total_seconds()) <= 120:
        return closest_idx
    return None

def fetch_and_process_data(target_timestamp):
    """Fetch Garmin data for the target date and process it."""
    debug_print("\n=== Fetching Garmin Data ===")
    
    # Convert target timestamp to Madrid timezone
    madrid_tz = pytz.timezone('Europe/Madrid')
    target_dt = pd.to_datetime(target_timestamp)
    
    # Handle timezone conversion properly
    if target_dt.tzinfo is None:
        target_dt = madrid_tz.localize(target_dt)
    else:
        target_dt = target_dt.astimezone(madrid_tz)
    
    # Calculate the two previous timestamps (4 minutes back)
    prev_dt_1 = target_dt - timedelta(minutes=2)  # 2 minutes before
    prev_dt_2 = target_dt - timedelta(minutes=4)  # 4 minutes before
    
    # Get all dates we need to fetch
    dates_to_fetch = set([
        target_dt.strftime('%Y-%m-%d'),
        prev_dt_1.strftime('%Y-%m-%d'),
        prev_dt_2.strftime('%Y-%m-%d')
    ])
    
    debug_print(f"Fetching Garmin data for dates: {', '.join(dates_to_fetch)}")
    
    # Fetch Garmin data for each date
    garmin_script = os.path.join(ROOT_DIR, 'data_processing/retrieval/last_x_days.py')
    for date in dates_to_fetch:
        subprocess.run(['python', garmin_script, '--target_date', date], check=True)
    debug_print("✅ Garmin data fetched successfully")
    
    # Convert to CSV
    json_to_csv_script = os.path.join(ROOT_DIR, 'data_processing/conversion/json_to_csv.py')
    subprocess.run(['python', json_to_csv_script], check=True)
    debug_print("✅ Garmin data converted to CSV")
    
    # Load and process the data
    garmin_file = os.path.join(ROOT_DIR, 'data/raw/garmin_health_data.json')
    garmin_data = load_garmin_data(garmin_file)
    processed_data = process_garmin_data(garmin_data)
    df = create_dataframe(processed_data)
    
    # Convert timestamps to Madrid timezone for comparison
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
    df['timestamp'] = df['timestamp'].dt.tz_convert(madrid_tz)
    
    # Find the closest timestamps for all three points
    debug_print("\n=== Timestamp Matching ===")
    debug_print(f"Looking for data points closest to:")
    debug_print(f"1. Target: {target_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    debug_print(f"2. Previous (2min): {prev_dt_1.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    debug_print(f"3. Previous (4min): {prev_dt_2.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Find closest indices for all three timestamps
    target_idx = find_closest_data_point(df, target_dt)
    prev_1_idx = find_closest_data_point(df, prev_dt_1)
    prev_2_idx = find_closest_data_point(df, prev_dt_2)
    
    if None in [target_idx, prev_1_idx, prev_2_idx]:
        debug_print("❌ Could not find all required timestamps in Garmin data")
        return None
    
    # Get all three rows
    rows = df.iloc[[prev_2_idx, prev_1_idx, target_idx]]
    debug_print("\nFound matching timestamps:")
    for i, (idx, row) in enumerate(rows.iterrows()):
        debug_print(f"{i+1}. {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Process the data through the feature engineering pipeline
    debug_print("\n=== Processing Features ===")
    
    # 1. Handle missing values
    debug_print("1. Handling missing values...")
    rows = handle_missing_values(rows)
    
    # 2. Add lag features
    debug_print("2. Adding lag features...")
    rows = add_lag_features(rows, rows.set_index('timestamp'))
    
    # 3. Encode categorical variables
    debug_print("3. Encoding categorical variables...")
    rows = encode_categorical_variables(rows)
    
    debug_print("✅ Feature processing complete")
    return rows.iloc[-1]  # Return only the target row

def round_timestamp(timestamp):
    """Round timestamp down to the nearest even minute."""
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    rounded_minute = (dt.minute // 2) * 2
    rounded_dt = dt.replace(minute=rounded_minute, second=0, microsecond=0)
    return rounded_dt.isoformat().replace('+00:00', 'Z')

def find_matching_timestamp(df, target_timestamp):
    """Find the row in the DataFrame that matches the target timestamp."""
    debug_print(f"\n=== Finding Matching Timestamp ===")
    debug_print(f"Target timestamp: {target_timestamp}")
    
    # Convert target timestamp to match DataFrame format
    target_dt = datetime.fromisoformat(target_timestamp.replace('Z', '+00:00'))
    
    # Convert DataFrame timestamps to local time for comparison
    df['local_timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize('UTC').dt.tz_convert('Europe/Madrid')
    target_dt_local = target_dt.astimezone(pytz.timezone('Europe/Madrid'))
    
    # Check if target timestamp is in the future
    most_recent = df['local_timestamp'].max()
    if target_dt_local > most_recent:
        debug_print(f"\nWarning: Requested timestamp {target_timestamp} is in the future.")
        debug_print(f"Using most recent available data from {most_recent}")
        return df[df['local_timestamp'] == most_recent].iloc[0]
    
    # Find matching row
    matching_row = df[df['local_timestamp'] == target_dt_local]
    
    if matching_row.empty:
        # Find the closest available timestamp
        time_diff = abs(df['local_timestamp'] - target_dt_local)
        closest_idx = time_diff.idxmin()
        closest_time = df.loc[closest_idx, 'local_timestamp']
        debug_print(f"\nWarning: No exact match for {target_timestamp}")
        debug_print(f"Using closest available timestamp: {closest_time}")
        return df.loc[closest_idx]
    
    debug_print("✅ Found exact timestamp match")
    return matching_row.iloc[0]

def prepare_features(data):
    """Prepare features for prediction."""
    debug_print("\n=== Preparing Features ===")
    debug_print("1. Selecting features...")
    
    # Define features for each model based on the final CSV files
    valence_features = [
        'heart_rate', 'respiration', 'body_battery', 'sleep_score', 
        'hr_change_now', 'time_Morning', 'time_Evening', 'time_Night'
    ]
    
    arousal_features = [
        'heart_rate', 'respiration', 'spo2', 'hrv_avg', 
        'hr_change_now', 'hr_change_2min', 'time_Morning', 'time_Afternoon'
    ]
    
    debug_print(f"Valence features: {valence_features}")
    debug_print(f"Arousal features: {arousal_features}")
    
    # Convert Series to DataFrame with a single row
    X_valence = pd.DataFrame([data[valence_features]])
    X_arousal = pd.DataFrame([data[arousal_features]])
    
    debug_print("\n2. Checking feature shapes...")
    debug_print(f"Valence features shape: {X_valence.shape}")
    debug_print(f"Arousal features shape: {X_arousal.shape}")
    
    debug_print("\n3. Checking feature values...")
    debug_print("Valence features:")
    debug_print(X_valence)
    debug_print("\nArousal features:")
    debug_print(X_arousal)
    
    debug_print("\n4. Checking for missing values...")
    debug_print("Valence features missing values:")
    debug_print(X_valence.isnull().sum())
    debug_print("\nArousal features missing values:")
    debug_print(X_arousal.isnull().sum())
    
    debug_print("\n5. Filling missing values...")
    # Fill missing values with 0
    X_valence = X_valence.fillna(0)
    X_arousal = X_arousal.fillna(0)
    
    # Convert all columns to float
    X_valence = X_valence.astype(float)
    X_arousal = X_arousal.astype(float)
    
    debug_print("✅ Features prepared")
    return X_valence, X_arousal

def predict_emotion(X_valence, X_arousal):
    """Predict valence and arousal using the trained models."""
    debug_print("\n=== Making Predictions ===")
    debug_print("1. Loading models and scalers...")
    try:
        # Load the scalers and models using absolute paths
        valence_scaler = joblib.load(os.path.join(ROOT_DIR, 'models', 'trained', 'valence_scaler.joblib'))
        arousal_scaler = joblib.load(os.path.join(ROOT_DIR, 'models', 'trained', 'arousal_scaler.joblib'))
        valence_model = joblib.load(os.path.join(ROOT_DIR, 'models', 'trained', 'best_valence_model.joblib'))
        arousal_model = joblib.load(os.path.join(ROOT_DIR, 'models', 'trained', 'best_arousal_model.joblib'))
        debug_print("✅ Models and scalers loaded")
        
        debug_print("\n2. Scaling features...")
        # Scale both valence and arousal features
        X_valence_scaled = valence_scaler.transform(X_valence)
        X_arousal_scaled = arousal_scaler.transform(X_arousal)
        debug_print("✅ Features scaled")
        
        debug_print("\n3. Making predictions...")
        # Make predictions
        valence = valence_model.predict(X_valence_scaled)[0]
        arousal = arousal_model.predict(X_arousal_scaled)[0]
        debug_print(f"Valence prediction: {valence}")
        debug_print(f"Arousal prediction: {arousal}")
        debug_print("✅ Predictions made")
        
        return valence, arousal
    except Exception as e:
        debug_print(f"\n❌ Error in predict_emotion: {str(e)}")
        raise

def determine_emotion(valence, arousal):
    """Determine the emotion based on valence and arousal values."""
    # Check if values are close to neutral
    if abs(valence) < 0.1 and abs(arousal) < 0.1:
        return "neutral"
    
    # Negative valence, positive arousal = red (frustrated/angry)
    if valence < 0 and arousal > 0:
        return "frustrated"
    
    # Negative valence, negative arousal = blue (sad/depressed)
    if valence < 0 and arousal < 0:
        return "sad"
    
    # Positive valence, negative arousal = yellow (calm/peaceful)
    if valence > 0 and arousal < 0:
        return "calm"
    
    # Positive valence, positive arousal = green (excited/happy)
    if valence > 0 and arousal > 0:
        return "excited"
    
    # Default to neutral if something unexpected happens
    return "neutral"

def main():
    parser = argparse.ArgumentParser(description='Predict emotion from Garmin data')
    parser.add_argument('timestamp', type=str, help='Timestamp in Madrid time (UTC+2)')
    args = parser.parse_args()
    
    try:
        # Fetch and process data
        data_point = fetch_and_process_data(args.timestamp)
        if data_point is None:
            print(json.dumps({"error": "No matching data point found"}))
            return
        
        # Prepare features
        X_valence, X_arousal = prepare_features(data_point)
        
        # Make predictions
        valence, arousal = predict_emotion(X_valence, X_arousal)
        
        # Determine emotion
        emotion = determine_emotion(valence, arousal)
        
        # Return results as JSON
        result = {
            'valence': float(valence),
            'arousal': float(arousal),
            'emotion': emotion,
            'timestamp': args.timestamp
        }
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main() 