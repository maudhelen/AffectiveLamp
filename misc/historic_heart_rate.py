from api.garmin_login import login_to_garmin
from datetime import datetime, timedelta
import json
import os 
from colorama import Fore, Style

DATA_DIR = "data/"
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure directory exists

def fetch_heart_rate_history():
    """Fetch heart rate history from today back to 100 days and save to JSON."""
    # Authenticate and get Garmin client
    client = login_to_garmin()

    if client:
        print("\nFetching real-time heart rate data. Press Ctrl+C to stop.\n")
        
        today = datetime.today()
        start_date = today - timedelta(days=75)

        heart_rate_data = {}
        
        print("Fetching heart rate history from", start_date.strftime("%Y-%m-%d"), "to", today.strftime("%Y-%m-%d"))

        for i in range(76):  # Including today (0 to 100 days back)
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            try:
                hr_data = client.get_heart_rates(date)  # Fetch heart rate data
                heart_rate_data[date] = hr_data if hr_data else "No Data"
                print(Fore.GREEN + f"Retrieved HR data for {date}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"Error fetching HR data for {date}: {e}" + Style.RESET_ALL)
                heart_rate_data[date] = "Error"

        # Save to JSON file
        json_filename = os.path.join(DATA_DIR, "heart_rate_history.json")
        with open(json_filename, "w") as json_file:
            json.dump(heart_rate_data, json_file, indent=4)

        print(Fore.CYAN + f"\nHeart rate history saved to {json_filename}" + Style.RESET_ALL)
        

    else:
        print("Could not log in to Garmin. Exiting.")
    
    

if __name__ == "__main__":
    fetch_heart_rate_history()
