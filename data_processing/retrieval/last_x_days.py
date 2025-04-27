"""
Fetches Garmin health data including:
- Heart Rate
- Stress
- Respiration Rate
- Sleep Score
- Body Battery
- SpO2
- HRV Average

Saves the data as `garmin_health_data.json`
"""
import os
import sys
import argparse

# Get the root directory path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add root directory to Python path
sys.path.append(ROOT_DIR)

# Set working directory to root
os.chdir(ROOT_DIR)
print("\nCurrent working directory: ", os.getcwd())

from api.garmin_login import login_to_garmin
from datetime import datetime, timedelta
import json
from colorama import Fore, Style

DATA_DIR = "data/raw/"
print(os.getcwd())

os.makedirs(DATA_DIR, exist_ok=True)  # Ensure directory exists
jsonfile = "garmin_health_data.json"

def fetch_garmin_health_data(days=75, target_date=None):
    # Authenticate and get Garmin client
    client = login_to_garmin()

    if client:
        print("\nFetching Garmin health data. Press Ctrl+C to stop.\n")

        if target_date:
            # If target_date is provided, fetch only that date
            today = datetime.strptime(target_date, "%Y-%m-%d")
            start_date = today
            days = 0  # Only fetch one day
            print(f"Fetching data for specific date: {target_date}")
        else:
            # Otherwise fetch the last X days
            today = datetime.today()
            start_date = today - timedelta(days=days)
            print(f"Fetching health data from {start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")

        health_data = {}

        for i in range(days + 1):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            try:
                # Fetch all required metrics
                hr_data = client.get_heart_rates(date)  # Heart Rate Data
                stress_data = client.get_stress_data(date)  # Stress Data
                respiration_data = client.get_respiration_data(date)  # Respiration Rate
                sleep_data = client.get_sleep_data(date)  # Sleep Data
                body_battery_data = client.get_body_battery(date)  # Body Battery
                sp02_data = client.get_spo2_data(date)  # SpO2 (Oxygen Saturation)
                hrv_data = client.get_hrv_data(date)

                # Extract sleep score from the nested structure
                sleep_score = None
                if sleep_data and isinstance(sleep_data, dict):
                    try:
                        sleep_score = (sleep_data
                            .get("dailySleepDTO", {})
                            .get("sleepScores", {})
                            .get("overall", {})
                            .get("value"))
                        print("Found sleep score")
                        print(sleep_score)
                    except (AttributeError, TypeError):
                        sleep_score = None

                # Extract heart rate values (timestamps & HR readings)
                heart_rate_values = hr_data.get("heartRateValues", None) if hr_data else None
                
                hrv_readings = hrv_data.get("hrvReadings", []) if hrv_data else []
                hrv_values = {entry["readingTimeGMT"]: entry["hrvValue"] for entry in hrv_readings} if hrv_readings else None
                
                # Get HRV average from the summary
                hrv_avg = hrv_data.get("hrvSummary", {}).get("lastNightAvg") if hrv_data else None
                
                # Store data for the date
                health_data[date] = {
                    "heart_rate": heart_rate_values if heart_rate_values else None,
                    "stress": stress_data if stress_data else None,
                    "respiration": respiration_data if respiration_data else None,
                    "sleep_score": sleep_score,
                    "body_battery": body_battery_data if body_battery_data else None,
                    "spo2": sp02_data if sp02_data else None,
                    "hrv": hrv_values if hrv_values else None,
                    "hrv_avg": hrv_avg
                }

                # If we have a sleep score, store it for the next day as well
                if sleep_score is not None:
                    next_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
                    if next_date not in health_data:
                        health_data[next_date] = {}
                    health_data[next_date]["previous_night_sleep_score"] = sleep_score

                print(Fore.GREEN + f"Retrieved health data for {date}" + Style.RESET_ALL)

            except Exception as e:
                print(Fore.RED + f"Error fetching data for {date}: {e}" + Style.RESET_ALL)
                health_data[date] = None

        # Save to JSON file
        json_filename = os.path.join(DATA_DIR, jsonfile)
        with open(json_filename, "w") as json_file:
            json.dump(health_data, json_file, indent=4)

        print(Fore.CYAN + f"\nHealth data saved to {json_filename}" + Style.RESET_ALL)

    else:
        print("Could not log in to Garmin. Exiting.")

if __name__ == "__main__":
    # Add command line argument for target date
    parser = argparse.ArgumentParser(description='Fetch Garmin health data')
    parser.add_argument('--target_date', type=str, help='Specific date to fetch data for (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=75, help='Number of days to fetch (default: 75)')
    args = parser.parse_args()
    
    fetch_garmin_health_data(days=args.days, target_date=args.target_date)
