import requests
import os
import math
import argparse
from dotenv import load_dotenv
from emotion_colors import get_emotion_color

# Load environment variables
load_dotenv()

# Get credentials from .env file
bridge_ip = os.getenv('BRIDGE_IP')
username = os.getenv('USERNAME')
light_id = 1  # ID of your light (e.g., 1, 2, 3)

def set_va_color(valence, arousal):
    """
    Set the light color based on Valence-Arousal coordinates
    
    Args:
        valence (float): Valence value (-1.0 to 1.0)
        arousal (float): Arousal value (0.0 to 1.0)
    """
    # Calculate distance from origin (0,0) for brightness
    distance = math.sqrt(valence**2 + arousal**2)
    normalized_distance = min(distance / math.sqrt(2), 1.0)  # Normalize to 0-1
    brightness = int(150 + (normalized_distance * 104))  # Scale to 150-254
    
    # Determine quadrant and set color
    if valence >= 0 and arousal >= 0.5:  # Q1: Happy/Excited
        xy = [0.409, 0.518]  # Green
    elif valence < 0 and arousal >= 0.5:  # Q2: Angry/Stressed
        xy = [0.675, 0.322]  # Red
    elif valence < 0 and arousal < 0.5:  # Q3: Sad/Depressed
        xy = [0.167, 0.04]   # Blue
    else:  # Q4: Calm/Relaxed
        xy = [0.418, 0.486]  # Yellow
    
    # Hue API uses xy color, brightness (0–254), on/off
    url = f"http://{bridge_ip}/api/{username}/lights/{light_id}/state"
    
    payload = {
        "on": True,
        "bri": brightness,
        "xy": xy
    }
    
    res = requests.put(url, json=payload)
    print(f"Setting light to VA coordinates ({valence}, {arousal}): {res.json()}")

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Control Philips Hue light based on emotion or VA coordinates')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--emotion', type=str, help='Emotion name (e.g., happy, sad)')
    group.add_argument('--va', nargs=2, type=float, metavar=('VALENCE', 'AROUSAL'),
                      help='Valence-Arousal coordinates (e.g., 0.8 0.8)')
    
    args = parser.parse_args()
    
    if args.emotion:
        set_emotion_color(args.emotion)
    elif args.va:
        valence, arousal = args.va
        set_va_color(valence, arousal)