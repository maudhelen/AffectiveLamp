import json
import random

# Define ranges for each emotion type
emotion_ranges = {
    "Happy": {
        "valence": (0.5, 0.9),    # Positive valence
        "arousal": (0.3, 0.7)     # Moderate to high arousal
    },
    "Excited": {
        "valence": (0.6, 0.9),    # High positive valence
        "arousal": (0.6, 0.9)     # High arousal
    },
    "Neutral": {
        "valence": (-0.2, 0.2),   # Near-zero valence
        "arousal": (-0.2, 0.2)    # Near-zero arousal
    },
    "Stressed": {
        "valence": (-0.7, -0.3),  # Negative valence
        "arousal": (0.6, 0.9)     # High arousal
    },
    "Anxious": {
        "valence": (-0.6, -0.2),  # Moderate negative valence
        "arousal": (0.5, 0.8)     # High arousal
    },
    "Angry": {
        "valence": (-0.9, -0.6),  # High negative valence
        "arousal": (0.6, 0.9)     # High arousal
    },
    "Annoyed": {
        "valence": (-0.7, -0.4),  # Moderate negative valence
        "arousal": (0.4, 0.7)     # Moderate arousal
    },
    "Sad": {
        "valence": (-0.9, -0.5),  # High negative valence
        "arousal": (-0.9, -0.5)   # Low arousal
    },
    "Tired": {
        "valence": (-0.4, -0.1),  # Slight negative valence
        "arousal": (-0.9, -0.6)   # Very low arousal
    },
    "Content": {
        "valence": (0.5, 0.8),    # Positive valence
        "arousal": (-0.4, -0.1)   # Slightly low arousal
    },
    "Pleased": {
        "valence": (0.4, 0.7),    # Moderate positive valence
        "arousal": (-0.3, 0.1)    # Near-neutral arousal
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