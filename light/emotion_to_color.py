from phue import Bridge
import os
from dotenv import load_dotenv
from pathlib import Path
import math
import requests
import time

def discover_bridge():
    """Discover the Hue bridge on the network"""
    try:
        response = requests.get("https://discovery.meethue.com/")
        bridges = response.json()
        if bridges:
            return bridges[0]['internalipaddress']
    except Exception as e:
        print(f"Error discovering bridge: {e}")
    return None

def connect_to_bridge():
    """Connect to the Hue bridge with automatic discovery"""
    # Load environment variables
    env_path = Path(__file__).resolve().parent / ".env"
    print(f"Loading .env from: {env_path}")
    load_dotenv(dotenv_path=env_path, override=True)
    
    # Try to get bridge IP from environment
    bridge_ip = os.getenv("BRIDGE_IP")
    print(f"Bridge IP from .env: {bridge_ip}")
    
    # If no IP in env or connection fails, try to discover bridge
    if not bridge_ip:
        print("No bridge IP in .env file, attempting to discover bridge...")
        bridge_ip = discover_bridge()
        if bridge_ip:
            print(f"Discovered bridge at {bridge_ip}")
            # Update .env file with new IP
            with open(env_path, 'w') as f:
                f.write(f"BRIDGE_IP={bridge_ip}\n")
        else:
            raise Exception("Could not discover bridge on network")
    
    # Try to connect to bridge
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to bridge at {bridge_ip} (attempt {attempt + 1}/{max_retries})")
            b = Bridge(bridge_ip)
            b.connect()
            print(f"Successfully connected to bridge at {bridge_ip}")
            return b
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                print("Retrying in 2 seconds...")
                time.sleep(2)
            else:
                raise Exception(f"Failed to connect to bridge after {max_retries} attempts: {e}")

# Connect to the bridge
b = connect_to_bridge()

def get_light():
    """Get the first available light"""
    lights = b.lights
    if not lights:
        raise Exception("No lights found")
    return lights[0]

def emotion_to_color(valence, arousal):
    """
    Convert valence and arousal values to Hue color coordinates (xy)
    
    Args:
        valence (float): -1.0 to 1.0 (negative to positive emotions)
        arousal (float): 0.0 to 1.0 (low to high intensity)
    
    Returns:
        tuple: (x, y) coordinates for the Hue light
    """
    # Normalize valence to 0-1 range
    normalized_valence = (valence + 1) / 2
    
    # Define color points in the emotional space
    # Colors are defined in the Hue xy color space
    colors = {
        # Basic colors
        "red": (0.675, 0.322),      # Bright red
        "green": (0.3, 0.599),    # Bright green
        "blue": (0.167, 0.04),      # Bright blue
        "yellow": (0.418, 0.486),   # Bright yellow
        "purple": (0.35, 0.168),    # Purple
        "cyan": (0.225, 0.332),     # Cyan
        "pink": (0.2638, 0.1167),   # Pink
        "white": (0.3227, 0.329),   # White
        
        # Emotional states
        "sad": (0.167, 0.04),       # Blue (low valence, low arousal)
        "angry": (0.675, 0.322),    # Red (low valence, high arousal)
        "calm": (0.443, 0.515),     # Yellow (high valence, low arousal)
        "happy": (0.409, 0.518),    # Green (high valence, high arousal)
        "excited": (0.35, 0.168),   # Purple (high arousal)
        "peaceful": (0.225, 0.332), # Cyan (low arousal)
    }
    
    # Interpolate between colors based on valence and arousal
    if normalized_valence < 0.5:
        # Negative emotions
        if arousal < 0.5:
            # Sad (blue)
            return colors["sad"]
        else:
            # Angry (red)
            return colors["angry"]
    else:
        # Positive emotions
        if arousal < 0.5:
            # Calm (yellow)
            return colors["calm"]
        else:
            # Happy (green)
            return colors["happy"]

def set_emotion(valence, arousal, brightness=255):
    """
    Set the light color based on emotional state
    
    Args:
        valence (float): -1.0 to 1.0 (negative to positive emotions)
        arousal (float): 0.0 to 1.0 (low to high intensity)
        brightness (int): 0-255 (light brightness)
    """
    light = get_light()
    light.on = True
    light.brightness = brightness
    light.xy = emotion_to_color(valence, arousal)

def set_color(color_name, brightness=255):
    """
    Set the light to a specific color by name
    
    Args:
        color_name (str): Name of the color to set
        brightness (int): 0-255 (light brightness)
    """
    colors = {
        "red": (0.675, 0.322),
        "green": (0.409, 0.518),
        "blue": (0.167, 0.04),
        "yellow": (0.443, 0.515),
        "purple": (0.35, 0.168),
        "cyan": (0.225, 0.332),
        "pink": (0.2638, 0.1167),
        "white": (0.3227, 0.329),
    }
    
    if color_name.lower() not in colors:
        raise ValueError(f"Color {color_name} not found. Available colors: {', '.join(colors.keys())}")
    
    light = get_light()
    light.on = True
    light.brightness = brightness
    light.xy = colors[color_name.lower()]

# Example usage:
if __name__ == "__main__":
    # Test different colors
    set_color("yellow")  # Set to yellow
    # set_color("red")    # Set to red
    # set_color("blue")   # Set to blue
    
    #sleep for 10 seconds
    time.sleep(5)
    set_color("green")  # Set to green
    # set_color("purple") # Set to purple
    # set_color("cyan")   # Set to cyan
    # set_color("pink")   # Set to pink
    # set_color("white")  # Set to white 