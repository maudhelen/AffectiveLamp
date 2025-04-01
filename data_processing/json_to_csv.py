import json
import pandas as pd
import os
from datetime import datetime, timezone


def json_to_csv(femotion, fgarmin, fcombined):
    # Define file paths
    DATA_DIR = "data/"
    emotion_file = os.path.join(DATA_DIR, femotion)
    garmin_file = os.path.join(DATA_DIR, fgarmin)
    csv_filename = os.path.join(DATA_DIR, fcombined)

    # Load emotion data
    with open(emotion_file, "r") as f:
        emotion_data = json.load(f)

    # Load Garmin health data
    with open(garmin_file, "r") as f:
        garmin_data = json.load(f)

    # Convert emotion timestamps to nearest even minute (rounding down)
    for entry in emotion_data:
        timestamp_dt = datetime.strptime(entry["timestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        rounded_minute = timestamp_dt.minute - (timestamp_dt.minute % 2)  # Round down to nearest even minute
        new_timestamp = timestamp_dt.replace(minute=rounded_minute, second=0, microsecond=0)
        entry["rounded_timestamp"] = new_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    # List to store merged data
    merged_data = []

    # Iterate through Garmin data (by date)
    for date, health in garmin_data.items():
        # Safely get heart rate values (if available)
        heart_rate_values = health.get("heart_rate", [])
        if not heart_rate_values:
            continue  # Skip days with no heart rate data

        # Convert heart rate timestamps to UTC
        hr_data = {
            datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"): hr
            for ts, hr in heart_rate_values
        }

        # Convert other signals to timestamp-based dictionaries
        def extract_time_series(data, key):
            """Extract timestamped values from nested structures safely."""
            if not data or key not in data or data[key] is None:
                return {}  # Return empty dict if key is missing or value is None
            return {
                datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"): value
                for ts, value in data[key]
            }


        stress_data = extract_time_series(health.get("stress", {}), "stressValuesArray")
        respiration_data = extract_time_series(health.get("respiration", {}), "respirationValuesArray")
        body_battery_data = extract_time_series(health.get("body_battery", [{}])[0], "bodyBatteryValuesArray")
        spo2_data = extract_time_series(health.get("spo2"), "spO2HourlyAverages")

        # Extract HRV readings
        hrv_data = {
            entry["readingTimeGMT"]: entry["hrvValue"]
            for entry in health.get("hrvReadings", [])
        }

        # Sleep Score (single value per day)
        sleep_score = health.get("sleep_score", "No Data")

        # Initialize last known values for less frequent signals
        last_stress, last_resp, last_body_battery, last_spo2, last_hrv = None, None, None, None, None

        # Merge data by timestamps
        for timestamp, heart_rate in hr_data.items():
            # Update last known values for less frequent signals
            last_stress = stress_data.get(timestamp, last_stress)
            last_resp = respiration_data.get(timestamp, last_resp)
            last_body_battery = body_battery_data.get(timestamp, last_body_battery)
            last_spo2 = spo2_data.get(timestamp, last_spo2)
            last_hrv = hrv_data.get(timestamp, last_hrv)

            # Find the closest emotion timestamp and assign the emotion
            matching_emotion = next((e["emotion"] for e in emotion_data if e["rounded_timestamp"] == timestamp), None)

            # Store merged data
            merged_data.append({
                "timestamp": timestamp,
                "heart_rate": heart_rate,
                "stress": last_stress,
                "respiration": last_resp,
                "body_battery": last_body_battery,
                "spo2": last_spo2,
                "hrv": last_hrv,
                "sleep_score": sleep_score,
                "emotion": matching_emotion if matching_emotion else "No Data"
            })

    # Convert to DataFrame
    df = pd.DataFrame(merged_data)

    # Save to CSV
    df.to_csv(csv_filename, index=False)

    print(f"✅ Combined data saved to {csv_filename}")
    return df
