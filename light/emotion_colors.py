# Emotion to color mappings based on Valence-Arousal (VA) values
# Valence: -1.0 (negative) to 1.0 (positive)
# Arousal: 0.0 (low) to 1.0 (high)

EMOTION_COLORS = {
    # Positive Valence, Positive Arousal
    "excited": {"xy": [0.409, 0.518], "bri": 254},   # Green
    "happy": {"xy": [0.409, 0.518], "bri": 254},     # Green
    
    # Positive Valence, Negative Arousal
    "calm": {"xy": [0.418, 0.486], "bri": 200},      # Yellow
    "peaceful": {"xy": [0.418, 0.486], "bri": 200},  # Yellow
    
    # Negative Valence, Positive Arousal
    "frustrated": {"xy": [0.675, 0.322], "bri": 254}, # Red
    "angry": {"xy": [0.675, 0.322], "bri": 254},     # Red
    
    # Negative Valence, Negative Arousal
    "sad": {"xy": [0.167, 0.04], "bri": 150},        # Blue
    "depressed": {"xy": [0.167, 0.04], "bri": 150},  # Blue
    
    # Neutral states - Pure white (D65 white point)
    "neutral": {"xy": [0.3127, 0.3290], "bri": 200}, # Pure white
    "focused": {"xy": [0.3127, 0.3290], "bri": 200}, # Pure white
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