import json
import time
import subprocess
import pandas as pd
from datetime import datetime

def run_prediction(timestamp):
    """Run the prediction script for a given timestamp"""
    try:
        # Run the prediction script and capture both stdout and stderr
        process = subprocess.run(
            ['python3', 'models/predict_emotion.py', timestamp],
            capture_output=True,
            text=True
        )
        
        # Print stderr for debugging
        if process.stderr:
            print(f"\nDebug output from prediction script:")
            print(process.stderr)
        
        # Check if the process failed
        if process.returncode != 0:
            print(f"\nPrediction script failed with return code {process.returncode}")
            print(f"Error output: {process.stderr}")
            return None
            
        # Get the last line of stdout (the prediction result)
        output_lines = [line for line in process.stdout.strip().split('\n') if line.strip()]
        if not output_lines:
            print(f"\nNo output from prediction script")
            return None
            
        last_line = output_lines[-1]
        try:
            prediction = json.loads(last_line)
            if "error" in prediction:
                print(f"\nPrediction error: {prediction['error']}")
                return None
            return prediction
        except json.JSONDecodeError as e:
            print(f"\nFailed to parse prediction result: {e}")
            print(f"Raw output: {last_line}")
            return None
            
    except Exception as e:
        print(f"\nError running prediction for {timestamp}: {e}")
        return None

def main():
    # Read the new_data.csv file
    try:
        df = pd.read_csv('data/new/new_data.csv', header=None)
        df.columns = ['timestamp', 'valence', 'arousal', 'emotion', 'hue', 'saturation', 'brightness']
    except Exception as e:
        print(f"Error reading new_data.csv: {e}")
        return
    
    results = []
    
    print("\n=== Starting Demo Predictions ===")
    print(f"Found {len(df)} timestamps to predict\n")
    
    for index, row in df.iterrows():
        timestamp = row['timestamp']
        actual_valence = row['valence']
        actual_arousal = row['arousal']
        actual_emotion = row['emotion']
        
        print(f"\nProcessing timestamp {index + 1}/{len(df)}: {timestamp}")
        print(f"Actual values - Valence: {actual_valence:.4f}, Arousal: {actual_arousal:.4f}, Emotion: {actual_emotion}")
        
        # Run prediction
        prediction = run_prediction(timestamp)
        
        if prediction:
            predicted_valence = prediction.get('valence')
            predicted_arousal = prediction.get('arousal')
            predicted_emotion = prediction.get('emotion')
            
            if all(v is not None for v in [predicted_valence, predicted_arousal, predicted_emotion]):
                # Calculate differences
                valence_diff = abs(actual_valence - predicted_valence)
                arousal_diff = abs(actual_arousal - predicted_arousal)
                
                print(f"Predicted values - Valence: {predicted_valence:.4f}, Arousal: {predicted_arousal:.4f}, Emotion: {predicted_emotion}")
                print(f"Differences - Valence: {valence_diff:.4f}, Arousal: {arousal_diff:.4f}")
                
                # Store results
                results.append({
                    'timestamp': timestamp,
                    'v_a': actual_valence,
                    'v_p': predicted_valence,
                    'a_a': actual_arousal,
                    'a_p': predicted_arousal,
                    'difference': valence_diff + arousal_diff,
                    'p_label': predicted_emotion,
                    'a_label': actual_emotion
                })
            else:
                print("Missing values in prediction result")
        else:
            print("Failed to get prediction")
        
        # Wait 10 seconds before next prediction
        if index < len(df) - 1:
            print("\nWaiting 1 second before next prediction...")
            time.sleep(1)
    
    # Save results to CSV
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv('data/predictions_demo.csv', index=False)
        print("\nResults saved to data/predictions_demo.csv")
        
        # Print summary
        print("\n=== Prediction Summary ===")
        print(f"Total predictions: {len(results)}")
        avg_difference = results_df['difference'].mean()
        print(f"Average total difference: {avg_difference:.4f}")

if __name__ == "__main__":
    main() 