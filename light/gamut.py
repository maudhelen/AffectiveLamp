import requests
import os

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

BRIDGE_IP = os.getenv('BRIDGE_IP')
USERNAME = os.getenv('USERNAME')

url = f"http://{BRIDGE_IP}/api/{USERNAME}/lights"
response = requests.get(url)
lights = response.json()

# Check each light's gamut
print("\nDetected Gamut Types:")
for light_id, light_info in lights.items():
    model_id = light_info['modelid']
    print(f"{light_info['name']} | Gamut: {light_info['capabilities']['control']['colorgamuttype']}")
