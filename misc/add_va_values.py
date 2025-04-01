import json
import random

# Define ranges based on the graph's values, adding variation while staying in correct quadrants
emotion_ranges = {
    "Happy": {
        "valence": (0.85, 1.0),      # Around 0.95
        "arousal": (0.4, 0.6)        # Around 0.5
    },
    "Excited": {
        "valence": (0.65, 0.85),     # Around 0.75
        "arousal": (0.75, 0.95)      # Around 0.85
    },
    "Confident": {
        "valence": (0.7, 0.9),       # Around 0.8
        "arousal": (0.1, 0.3)        # Around 0.2
    },
    "Pleased": {
        "valence": (1.0, 1.2),       # Around 1.1
        "arousal": (-0.25, -0.05)    # Around -0.15
    },
    "Content": {
        "valence": (0.65, 0.85),     # Around 0.75
        "arousal": (-0.55, -0.35)    # Around -0.45
    },
    "Anxious": {
        "valence": (-0.8, -0.6),     # Around -0.7
        "arousal": (0.9, 1.1)        # Around 1.0
    },
    "Angry": {
        "valence": (-1.0, -0.8),     # Around -0.9
        "arousal": (0.59, 0.79)      # Around 0.69
    },
    "Annoyed": {
        "valence": (-1.05, -0.85),   # Around -0.95
        "arousal": (0.35, 0.55)      # Around 0.45
    },
    "Sad": {
        "valence": (-1.1, -0.9),     # Around -1.0
        "arousal": (-0.65, -0.45)    # Around -0.55
    },
    "Tired": {
        "valence": (-0.3, -0.1),     # Around -0.2
        "arousal": (-1.2, -1.0)      # Around -1.1
    },
    "Neutral": {
        "valence": (-0.1, 0.1),      # Around 0.0
        "arousal": (-0.1, 0.1)       # Around 0.0
    }
}

def add_va_values():
    # Read the existing JSON file
    with open('data/emotion_data.json', 'r') as f:
        data = json.load(f)
    
    # Add VA values for each entry
    for entry in data:
        emotion = entry['emotion']
        # If emotion not in our ranges, treat as neutral
        ranges = emotion_ranges.get(emotion, emotion_ranges['Neutral'])
        
        # Generate random values within the appropriate ranges
        entry['valence'] = round(random.uniform(
            ranges['valence'][0], 
            ranges['valence'][1]
        ), 2)
        entry['arousal'] = round(random.uniform(
            ranges['arousal'][0], 
            ranges['arousal'][1]
        ), 2)
    
    # Save the updated data
    with open('data/emotion_data.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    add_va_values()