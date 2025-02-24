import os
from pathlib import Path
from dotenv import load_dotenv
from garminconnect import Garmin, GarminConnectAuthenticationError, GarminConnectConnectionError, GarminConnectTooManyRequestsError
from colorama import Fore, Style
import json

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Get credentials
EMAIL = os.getenv("GARMIN_EMAIL")
PASSWORD = os.getenv("GARMIN_PASSWORD")

# Define token storage path
TOKEN_PATH = os.path.expanduser("~/.garminconnect")


def login_to_garmin():
    """Authenticate and return a Garmin client instance with token persistence."""
    
    # Check if token file exists
    if os.path.exists(TOKEN_PATH):
        try:
            client = Garmin()
            client.login(TOKEN_PATH)
            print(Fore.GREEN +"Logged in using stored token!" + Style.RESET_ALL)
            return client
        except Exception as e:
            print(Fore.RED + f"Token login failed, re-authenticating: {e}" + Style.RESET_ALL)

    if not EMAIL or not PASSWORD:
        raise ValueError("Missing Garmin credentials. Set GARMIN_EMAIL and GARMIN_PASSWORD.")

    print("Logging in with credentials...")

    try:
        client = Garmin(EMAIL, PASSWORD)
        client.login()
        client.garth.dump(TOKEN_PATH)
        print("Garmin client created and token saved.")
        return client

    except GarminConnectAuthenticationError:
        print(Fore.RED + "Garmin authentication error. Check your credentials."+ Style.RESET_ALL)
    except GarminConnectConnectionError:
        print(Fore.RED + "Garmin connection error. Check your internet connection."+ Style.RESET_ALL)
    except GarminConnectTooManyRequestsError:
        print(Fore.RED + "Too many login attempts. Try again later."+ Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Unexpected error: {e}"+ Style.RESET_ALL)

    return None 

def display_json(api_call, output):
    """Format API output for better readability."""

    dashed = "-" * 20
    header = f"{dashed} {api_call} {dashed}"
    footer = "-" * len(header)

    print(header)

    if isinstance(output, (int, str, dict, list)):
        print(json.dumps(output, indent=4))
    else:
        print(output)

    print(footer)


if __name__ == "__main__":
    login_to_garmin()