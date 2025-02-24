import json
import pandas as pd
import os
from colorama import Fore, Style

# Load the JSON data
JSON_FILE_PATH = "data/heart_rate_json/heart_rate_history.json"
OUTPUT_DIR = "data/heart_rate_csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(JSON_FILE_PATH, "r") as json_file:
    heart_rate_data = json.load(json_file)

print(Fore.GREEN + "✅ JSON data loaded successfully." + Style.RESET_ALL)

# Convert JSON to DataFrame
data_list = []

for date, values in heart_rate_data.items():
    if isinstance(values, dict):  # Ensure it's a dictionary with data
        # Extract general heart rate info
        entry = {
            "Date": date,
            "UserProfilePK": values.get("userProfilePK"),
            "CalendarDate": values.get("calendarDate"),
            "StartTimestampGMT": values.get("startTimestampGMT"),
            "EndTimestampGMT": values.get("endTimestampGMT"),
            "StartTimestampLocal": values.get("startTimestampLocal"),
            "EndTimestampLocal": values.get("endTimestampLocal"),
            "MaxHeartRate": values.get("maxHeartRate"),
            "MinHeartRate": values.get("minHeartRate"),
            "RestingHeartRate": values.get("restingHeartRate"),
            "LastSevenDaysAvgRestingHeartRate": values.get("lastSevenDaysAvgRestingHeartRate"),
        }
        
        # Extract detailed heart rate values if available
        heart_rate_values = values.get("heartRateValues")
        if heart_rate_values:  # Check if heartRateValues is not None
            for hr_entry in heart_rate_values:
                timestamp, heart_rate = hr_entry
                data_list.append({**entry, "Timestamp": timestamp, "HeartRate": heart_rate})
        else:
            # Add a placeholder entry if no heart rate data exists
            data_list.append({**entry, "Timestamp": None, "HeartRate": None})

# Create DataFrame
df = pd.DataFrame(data_list)

# Define CSV file path
csv_file_path = os.path.join(OUTPUT_DIR, "heart_rate_history.csv")
os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)  # Ensure directory exists

# Save DataFrame to CSV
df.to_csv(csv_file_path, index=False)

print(Fore.GREEN + f"📁 CSV saved successfully to {csv_file_path}" + Style.RESET_ALL)
