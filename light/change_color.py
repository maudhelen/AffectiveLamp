import requests
import os
from dotenv import load_dotenv
from emotion_colors import get_emotion_color

# Load environment variables
load_dotenv()

# Get credentials from .env file
bridge_ip = os.getenv('BRIDGE_IP')
username = os.getenv('USERNAME')
light_id = 1  # ID of your light (e.g., 1, 2, 3)

def set_emotion_color(emotion):
    """
    Set the light color based on the given emotion
    
    Args:
        emotion (str): The emotion name (e.g., 'happy', 'sad', 'calm')
    """
    # Get color settings for the emotion
    color_settings = get_emotion_color(emotion)
    
    # Hue API uses xy color, brightness (0–254), on/off
    url = f"http://{bridge_ip}/api/{username}/lights/{light_id}/state"
    
    payload = {
        "on": True,
        "bri": color_settings["bri"],
        "xy": color_settings["xy"]
    }
    
    res = requests.put(url, json=payload)
    print(f"Setting light to {emotion} color: {res.json()}")

# Example usage:
if __name__ == "__main__":
    # Test with different emotions
    # set_emotion_color("happy")  # Set to happy (green)
    # set_emotion_color("sad")    # Set to sad (blue)
    # set_emotion_color("calm")   # Set to calm (yellow)
    set_emotion_color("angry")  # Set to angry (red)