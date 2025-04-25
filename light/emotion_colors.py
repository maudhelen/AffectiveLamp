# Emotion to color mappings based on Valence-Arousal (VA) values
# Valence: -1.0 (negative) to 1.0 (positive)
# Arousal: 0.0 (low) to 1.0 (high)

EMOTION_COLORS = {
    # High Valence, High Arousal
    "excited": {"xy": [0.35, 0.168], "bri": 254},  # Purple
    "happy": {"xy": [0.409, 0.518], "bri": 254},   # Green
    "joyful": {"xy": [0.409, 0.518], "bri": 254},  # Green
    
    # High Valence, Low Arousal
    "calm": {"xy": [0.418, 0.486], "bri": 200},    # Yellow
    "peaceful": {"xy": [0.225, 0.332], "bri": 180}, # Cyan
    "content": {"xy": [0.443, 0.515], "bri": 200},  # Yellow
    
    # Low Valence, High Arousal
    "angry": {"xy": [0.675, 0.322], "bri": 254},   # Red
    "frustrated": {"xy": [0.675, 0.322], "bri": 254}, # Red
    "anxious": {"xy": [0.675, 0.322], "bri": 254}, # Red
    
    # Low Valence, Low Arousal
    "sad": {"xy": [0.167, 0.04], "bri": 150},      # Blue
    "depressed": {"xy": [0.167, 0.04], "bri": 150}, # Blue
    "tired": {"xy": [0.167, 0.04], "bri": 150},    # Blue
    
    # Neutral states
    "neutral": {"xy": [0.3227, 0.329], "bri": 200}, # White
    "focused": {"xy": [0.3227, 0.329], "bri": 200}, # White
}

def get_emotion_color(emotion):
    """
    Get the color settings for a given emotion
    
    Args:
        emotion (str): The emotion name (must be in EMOTION_COLORS)
    
    Returns:
        dict: Color settings with 'xy' and 'bri' values
    """
    emotion = emotion.lower()
    if emotion not in EMOTION_COLORS:
        raise ValueError(f"Emotion '{emotion}' not found. Available emotions: {', '.join(EMOTION_COLORS.keys())}")
    return EMOTION_COLORS[emotion] 