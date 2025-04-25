import os
import pandas as pd
import numpy as np
from pathlib import Path

def setup_data_path():
    """Set up the data directory path."""
    DATA_DIR = os.path.join(os.getcwd(), 'data')
    print(f"Data directory: {DATA_DIR}")
    print(os.listdir(DATA_DIR))
    return DATA_DIR

def load_data(DATA_DIR):
    """Load and preprocess the data."""
    data = pd.read_csv(DATA_DIR + '/merged/labelled_data.csv')
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    return data

def handle_missing_values(data):
    """Handle missing values in the dataset."""
    # Fill missing sleep scores with median
    data['sleep_score'] = data['sleep_score'].fillna(data['sleep_score'].median())
    
    # Create sleep score tiers
    data['sleep_score_tier'] = pd.cut(data['sleep_score'], 
                                    bins=[0, 50, 70, 90, 100], 
                                    labels=['Poor', 'Fair', 'Good', 'Excellent'])
    
    # Fill missing HRV values based on sleep score tiers
    data['hrv_avg'] = data['hrv_avg'].fillna(data.groupby('sleep_score_tier')['hrv_avg'].transform('mean'))
    
    # Fill missing SpO2 values with median
    data['spo2'] = data['spo2'].fillna(data['spo2'].median())
    
    # Create time of day column
    data['time_of_day'] = pd.cut(data['timestamp'].dt.hour, 
                                bins=[0, 6, 12, 18, 22, 24], 
                                labels=['Night', 'Morning', 'Afternoon', 'Evening', 'Night'],
                                include_lowest=True,
                                ordered=False)
    
    # Fill missing body battery values based on time of day
    data['body_battery'] = data['body_battery'].fillna(data.groupby('time_of_day')['body_battery'].transform('mean'))
    
    # Drop any remaining missing values
    data = data.dropna()
    
    # Round all float columns to 2 decimal places
    data = data.round(2)
    
    return data

def save_cleaned_data(data, DATA_DIR):
    """Save the cleaned data to a CSV file."""
    data.to_csv(DATA_DIR + "/new/cleaned_data.csv", index=False)
    print("Cleaned data saved successfully!")

def main():
    """Main function to run the data cleaning pipeline."""
    # Set up data path
    DATA_DIR = setup_data_path()
    
    # Load data
    data = load_data(DATA_DIR)
    
    # Handle missing values
    data = handle_missing_values(data)
    
    # Save cleaned data
    save_cleaned_data(data, DATA_DIR)

if __name__ == "__main__":
    main() 