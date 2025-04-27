import os
import sys
import json
import requests
import time

# Get the root directory path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add root directory to Python path
sys.path.append(ROOT_DIR)

# Set working directory to root
os.chdir(ROOT_DIR)

# Load bridge configuration
bridge_path = os.path.join(ROOT_DIR, 'light', 'bridge.json')
with open(bridge_path, 'r') as f:
    bridge_configs = json.load(f)
    bridge_config = bridge_configs[0]

BRIDGE_IP = bridge_config['internalipaddress']

def create_username():
    """
    Create a new username for the Hue bridge
    """
    print("Press the link button on your Hue bridge now...")
    print("You have 30 seconds to press the button...")
    
    # Wait for user to press the button
    time.sleep(5)
    
    # Create the username
    url = f"http://{BRIDGE_IP}/api"
    data = {
        "devicetype": "AffectiveLamp#python"
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()[0]
        if 'success' in result:
            username = result['success']['username']
            print(f"Successfully created username: {username}")
            
            # Update the bridge configuration
            bridge_config['id'] = username
            with open(bridge_path, 'w') as f:
                json.dump([bridge_config], f, indent=4)
            
            print(f"Updated bridge configuration in {bridge_path}")
            return username
        else:
            print("Error creating username:", result.get('error', {}).get('description', 'Unknown error'))
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    create_username() 