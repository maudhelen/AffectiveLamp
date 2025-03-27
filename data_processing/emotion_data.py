import json
import os

emotion_data = [
    {
        "timestamp": "2025-02-24T19:05:00Z",
        "emotion": "Happy"
    },
    {
        "timestamp": "2025-02-24T18:12:00Z",
        "emotion": "Happy"
    },
    {
        "timestamp": "2025-02-24T17:32:00Z",
        "emotion": "Happy"
    },
    {
        "timestamp": "2025-02-25T19:05:00Z",
        "emotion": "Excited"
    },
    {
        "timestamp": "2025-02-25T16:53:00Z",
        "emotion": "Neutral"
    },
    {
        "timestamp": "2025-02-25T15:09:00Z",
        "emotion": "Stressed"
    },
    {
        "timestamp": "2025-02-25T14:53:00Z",
        "emotion": "Happy"
    },
    {
        "timestamp": "2025-02-25T14:30:00Z",
        "emotion": "Angry"
    },
    {
        "timestamp": "2025-02-25T14:30:00Z",
        "emotion": "Annoyed"
    },
    {
        "timestamp": "2025-02-25T12:37:00Z",
        "emotion": "Angry"
    },
    {
        "timestamp": "2025-02-25T12:37:00Z",
        "emotion": "Upset"
    },
    {
        "timestamp": "2025-02-25T12:12:00Z",
        "emotion": "Neutral"
    },
    {
        "timestamp": "2025-02-26T09:54:00Z",
        "emotion": "Neutral"
    },
    {
        "timestamp": "2025-02-26T11:26:00Z",
        "emotion": "Neutral"
    },
    {
        "timestamp": "2025-02-26T16:19:00Z",
        "emotion": "Angry"
    },
    {
        "timestamp": "2025-02-27T10:37:00Z",
        "emotion": "Neutral"
    },
    {
        "timestamp": "2025-02-27T11:20:00Z",
        "emotion": "Happy"
    },
    {
        "timestamp": "2025-02-27T14:52:00Z",
        "emotion": "Stressed"
    },
    {
        "timestamp": "2025-02-27T15:12:00Z",
        "emotion": "Stressed"
    },
    {
        "timestamp": "2025-02-27T16:23:00Z",
        "emotion": "Stressed"
    },
    {
        "timestamp": "2025-02-27T18:29:00Z",
        "emotion": "Neutral"
    },
    {
        "timestamp": "2025-02-27T22:29:00Z",
        "emotion": "Neutral"
    },
    {
        "timestamp": "2025-02-28T16:48:00Z",
        "emotion": "Happy"
    },
    {
        "timestamp": "2025-03-03T10:48:00Z",
        "emotion": "Neutral"
    },
    {
        "timestamp": "2025-03-04T13:34:00Z",
        "emotion": "Sad"
    },
    {
        "timestamp": "2025-03-04T12:35:00Z",
        "emotion": "Sad"
    },
    {
        "timestamp": "2025-03-06T14:49:00Z",
        "emotion": "Sad"
    },
    {
        "timestamp": "2025-03-07T16:07:00Z",
        "emotion": "Sad"
    },
    {
        "timestamp": "2025-03-07T15:00:00Z",
        "emotion": "Neutral"
    },
    {
        "timestamp": "2025-03-07T12:25:00Z",
        "emotion": "Sad"
    },
    {
        "timestamp": "2025-03-07T10:20:00Z",
        "emotion": "Happy"
    },
    {
        "timestamp": "2025-03-19T15:52:00Z",
        "emotion": "Neutral"
    },
]

# Define the save path
DATA_DIR = "data/"
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure directory exists
json_filename = os.path.join(DATA_DIR, "emotion_data.json")

# Save to JSON file
with open(json_filename, "w") as json_file:
    json.dump(emotion_data, json_file, indent=4)

print(f"Emotion data saved to {json_filename}")