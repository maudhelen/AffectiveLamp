import json
import pandas as pd
import os
from datetime import datetime, timezone
import pytz
import sys

def load_garmin_data(garmin_file):
    """Load Garmin health data from JSON file."""
    with open(garmin_file, "r") as f:
        garmin_data = json.load(f)
    print("✅ Loaded Garmin health data")
    return garmin_data

def process_garmin_data(garmin_data):
    """Process Garmin health data into a structured format."""
    processed_data = []

    # Iterate through Garmin data (by date)
    for date, health in garmin_data.items():
        # Safely get heart rate values
        heart_rate_values = health.get("heart_rate", [])
        if not heart_rate_values:
            continue  # Skip days with no heart rate data

        # Convert heart rate timestamps to UTC
        hr_data = {
            datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"): hr
            for ts, hr in heart_rate_values
        }

        # Helper function for extracting time series data
        def extract_time_series(data, key):
            if not data or key not in data or data[key] is None:
                return {}
            return {
                datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"): value
                for ts, value in data[key]
            }

        # Extract all health metrics
        stress_data = extract_time_series(health.get("stress", {}), "stressValuesArray")
        respiration_data = extract_time_series(health.get("respiration", {}), "respirationValuesArray")
        body_battery_data = extract_time_series(health.get("body_battery", [{}])[0], "bodyBatteryValuesArray")
        spo2_data = extract_time_series(health.get("spo2"), "spO2HourlyAverages")
        hrv_avg = health.get("hrv_avg", {})

        # Extract HRV readings
        hrv_data = {
            entry["readingTimeGMT"]: entry["hrvValue"]
            for entry in health.get("hrvReadings", [])
        }

        # Get sleep score
        sleep_score = health.get("sleep_score")

        # Initialize last known values
        last_stress = last_resp = last_body_battery = last_spo2 = last_hrv = None

        # Merge data by timestamps
        for timestamp, heart_rate in hr_data.items():
            # Update last known values
            last_stress = stress_data.get(timestamp, last_stress)
            last_resp = respiration_data.get(timestamp, last_resp)
            last_body_battery = body_battery_data.get(timestamp, last_body_battery)
            last_spo2 = spo2_data.get(timestamp, last_spo2)
            last_hrv = hrv_data.get(timestamp, last_hrv)

            # Store processed data
            processed_data.append({
                "timestamp": timestamp,
                "heart_rate": heart_rate,
                "stress": last_stress,
                "respiration": last_resp,
                "body_battery": last_body_battery,
                "spo2": last_spo2,
                "sleep_score": sleep_score,
                "hrv_avg": hrv_avg
            })

    print("✅ Processed Garmin health data")
    return processed_data

def create_dataframe(processed_data):
    """Create and process DataFrame from processed data."""
    df = pd.DataFrame(processed_data)

    # Add local time column
    df['local_time'] = df['timestamp'].apply(lambda x: 
        datetime.strptime(x, "%Y-%m-%d %H:%M:%SZ")
        .replace(tzinfo=timezone.utc)
        .astimezone(pytz.timezone('Europe/Madrid')) 
        .strftime("%Y-%m-%d %H:%M:%S")
    )

    # Print dataset info
    print("\nDataset shape:", df.shape)
    print("\nSummary statistics:")
    print(df.describe())
    print("\nMissing values:")
    print(df.isnull().sum())

    return df

def main():
    # Get the root directory path
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Add root directory to Python path
    sys.path.append(ROOT_DIR)

    # Set working directory to root
    os.chdir(ROOT_DIR)

    # Define file paths
    DATA_DIR = "data/"
    garmin_file = os.path.join(DATA_DIR, "raw/garmin_health_data.json")
    csv_filename = os.path.join(DATA_DIR, "processed/garmin_data.csv")

    # Process data
    garmin_data = load_garmin_data(garmin_file)
    processed_data = process_garmin_data(garmin_data)
    df = create_dataframe(processed_data)

    # Save to CSV
    df.to_csv(csv_filename, index=False)
    print(f"✅ Garmin health data saved to {csv_filename}")

if __name__ == "__main__":
    main() 