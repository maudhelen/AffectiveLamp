import os
from pathlib import Path
from dotenv import load_dotenv

from garminconnect import Garmin, GarminConnectConnectionError, GarminConnectTooManyRequestsError, GarminConnectAuthenticationError

env_path = Path(__file__).resolve().parent.parent / ".env"

# print(
#     f"Loading environment variables from {env_path}. "
#     "Make sure this file exists and is properly configured."
# )

load_dotenv(dotenv_path=env_path)

# Get credentials from GitHub Secrets
EMAIL = os.getenv("GARMIN_EMAIL")
PASSWORD = os.getenv("GARMIN_PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("Missing Garmin credentials. Set GARMIN_EMAIL and GARMIN_PASSWORD.")

else:
    print("Garmin credentials found.")
    
try:
    client = Garmin(EMAIL, PASSWORD)
    client.login()
    print("Garmin client created.")
    
    user_info = client.get_full_name()
    print("\nUser info retrieved for user:")
    print(user_info)
    
except GarminConnectAuthenticationError:
    print("Garmin authentication error.")
except GarminConnectConnectionError:
    print("Garmin connection error.")
except GarminConnectTooManyRequestsError:
    print("Garmin too many requests error.")
except Exception as e:
    print(f"An error occurred: {e}")
    