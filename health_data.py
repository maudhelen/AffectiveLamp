"""
Fetches Garmin health data including:
- Heart Rate
- Stress
- Respiration Rate
- Sleep Score
- Body Battery
- SpO2

Saves the data as `garmin_health_data.json`
"""

from api.garmin_login import login_to_garmin
from datetime import datetime, timedelta
import json
import os
from colorama import Fore, Style

DATA_DIR = "data/"
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure directory exists

def fetch_garmin_health_data():
    """Fetch health data from today back to 75 days and save to JSON."""
    # Authenticate and get Garmin client
    client = login_to_garmin()
    days = 100

    if client:
        print("\nFetching Garmin health data. Press Ctrl+C to stop.\n")

        today = datetime.today()
        start_date = today - timedelta(days=days)

        health_data = {}

        print("Fetching health data from", start_date.strftime("%Y-%m-%d"), "to", today.strftime("%Y-%m-%d"))

        for i in range(days + 1):  # Including today (0 to 75 days back)
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

                # Extract sleep score (if available)
                sleep_score = sleep_data.get("sleepScore", "No Data") if sleep_data else "No Data"

                # Extract heart rate values (timestamps & HR readings)
                heart_rate_values = hr_data.get("heartRateValues", "No Data") if hr_data else "No Data"
                
                hrv_readings = hrv_data.get("hrvReadings", []) if hrv_data else []

                # Convert HRV readings to a timestamped dictionary
                hrv_values = {entry["readingTimeGMT"]: entry["hrvValue"] for entry in hrv_readings}

                # Store data for the date
                health_data[date] = {
                    "heart_rate": heart_rate_values,
                    "stress": stress_data if stress_data else "No Data",
                    "respiration": respiration_data if respiration_data else "No Data",
                    "sleep_score": sleep_score,
                    "body_battery": body_battery_data if body_battery_data else "No Data",
                    "spo2": sp02_data if sp02_data else "No Data",
                    "hrv": hrv_values if hrv_values else "No Data",
                }

                print(Fore.GREEN + f"Retrieved health data for {date}" + Style.RESET_ALL)

            except Exception as e:
                print(Fore.RED + f"Error fetching data for {date}: {e}" + Style.RESET_ALL)
                health_data[date] = "Error"

        # Save to JSON file
        json_filename = os.path.join(DATA_DIR, "garmin_health_data.json")
        with open(json_filename, "w") as json_file:
            json.dump(health_data, json_file, indent=4)

        print(Fore.CYAN + f"\nHealth data saved to {json_filename}" + Style.RESET_ALL)

    else:
        print("Could not log in to Garmin. Exiting.")

if __name__ == "__main__":
    fetch_garmin_health_data()
