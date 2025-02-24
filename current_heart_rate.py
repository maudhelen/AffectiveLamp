import os
from dotenv import load_dotenv
from colorama import Fore, Style
from datetime import datetime, date 
from api.garmin_login import login_to_garmin
import json

# Load environment variables
load_dotenv()
today = date.today()

def get_current_heart_rate():
    """Fetch the latest heart rate measurement from Garmin Connect."""
    try:
        client = login_to_garmin()
        print(Fore.GREEN + "Logged in successfully." + Style.RESET_ALL)

        heart_rate_data = client.get_stats(today)  # Try fetching user stats

        print(json.dumps(heart_rate_data, indent=4))
        
        if heart_rate_data and "restingHeartRate" in heart_rate_data:
            latest_hr = heart_rate_data.get("restingHeartRate")
            print(Fore.CYAN + f"Current Heart Rate: {latest_hr} BPM" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "No real-time heart rate data available." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"Error fetching heart rate: {e}" + Style.RESET_ALL)

if __name__ == "__main__":
    get_current_heart_rate()
