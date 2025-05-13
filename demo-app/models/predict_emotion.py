import argparse
import json
import sys

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
        
        # Print all available features and their values
        debug_print("\n=== Available Features and Values ===")
        for col in data_point.index:
            if col != 'timestamp':
                debug_print(f"{col}: {data_point[col]}")
        
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