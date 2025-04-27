import os
import sys
import json
import requests

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
USERNAME = bridge_config['id']
LIGHT_ID = 1  # Default to first light

def get_va_color(valence, arousal):
    """
    Get color based on VA values
    - LALV (Low Arousal Low Valence) = Blue
    - HALV (High Arousal Low Valence) = Red
    - HAHV (High Arousal High Valence) = Green
    - LAHV (Low Arousal High Valence) = Yellow
    - Center (within 0.3 radius) = White
    """
    # Check if values are within 0.3 radius of center
    if abs(valence) <= 0.3 and abs(arousal) <= 0.3:
        return {"xy": [0.3127, 0.3290], "bri": 200}
    
    # High Arousal, High Valence = Green
    if arousal > 0 and valence > 0:
        return {"xy": [0.409, 0.518], "bri": 254}
    
    # High Arousal, Low Valence = Red
    elif arousal > 0 and valence < 0:
        return {"xy": [0.675, 0.322], "bri": 254}
    
    # Low Arousal, Low Valence = Blue
    elif arousal < 0 and valence < 0:
        return {"xy": [0.167, 0.04], "bri": 150}
    
    # Low Arousal, High Valence = Yellow
    elif arousal < 0 and valence > 0:
        return {"xy": [0.418, 0.486], "bri": 200}
    
    # Default to neutral (white) if values are close to 0
    return {"xy": [0.3127, 0.3290], "bri": 200}

def change_light_color(valence, arousal):
    """
    Change the light color based on VA values
    """
    try:
        # Get color settings
        color_settings = get_va_color(valence, arousal)
        
        # Prepare the API request
        url = f"http://{BRIDGE_IP}/api/{USERNAME}/lights/{LIGHT_ID}/state"
        data = {
            "on": True,
            "xy": color_settings["xy"],
            "bri": color_settings["bri"],
            "transitiontime": 10
        }
        
        # Send the request
        response = requests.put(url, json=data)
        
        # Check for errors in the response
        response_data = response.json()
        if isinstance(response_data, list) and len(response_data) > 0:
            if 'error' in response_data[0]:
                print(f"Error from bridge: {response_data[0]['error']}")
                return False
        
        response.raise_for_status()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error controlling light: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python change_color.py <valence> <arousal>")
        sys.exit(1)
    
    try:
        valence = float(sys.argv[1])
        arousal = float(sys.argv[2])
        success = change_light_color(valence, arousal)
        if not success:
            print("Failed to change light color")
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)