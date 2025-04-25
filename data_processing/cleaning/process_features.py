import os
import pandas as pd
import numpy as np
from pathlib import Path

def setup_data_path():
    """Set up the data directory path."""
    DATA_DIR = os.path.join(os.getcwd(), 'data')
    print(f"Data directory: {DATA_DIR}")
    return DATA_DIR

def load_data(DATA_DIR, file_name):
    """Load both cleaned and merged datasets."""
    # Load cleaned data
    cleaned_data = pd.read_csv(os.path.join(DATA_DIR, 'new', file_name))
    cleaned_data['timestamp'] = pd.to_datetime(cleaned_data['timestamp']).dt.tz_localize(None)
    cleaned_data['timestamp'] = cleaned_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Load merged data for lag features
    garmin_data = pd.read_csv(os.path.join(DATA_DIR, 'processed', 'garmin_data.csv'), parse_dates=['timestamp'])
    
    #make local_time column in garmin_data the timestamp column and drop the timestamp column
    garmin_data = garmin_data.drop(columns=['timestamp'])
    garmin_data = garmin_data.rename(columns={'local_time': 'timestamp'})
    garmin_data['timestamp'] = pd.to_datetime(garmin_data['timestamp']).dt.tz_localize(None)
    garmin_data['timestamp'] = garmin_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    garmin_data.set_index('timestamp', inplace=True)
    
    return cleaned_data, garmin_data

def add_lag_features(cleaned_data, garmin_data):
    """Add lag features for heart rate."""
    # Create lag features
    lag_features = pd.DataFrame(index=garmin_data.index)
    lag_features['hr_1'] = garmin_data['heart_rate'].shift(1)  # 2 minutes ago
    lag_features['hr_2'] = garmin_data['heart_rate'].shift(2)  # 4 minutes ago
    lag_features.reset_index(inplace=True)
    
    # Merge lag features with cleaned data
    data = pd.merge(
        cleaned_data,
        lag_features,
        on='timestamp',
        how='left'
    )
    
    data['hr_change_now'] = data['heart_rate'] - data['hr_1']
    data['hr_change_2min'] = data['hr_2'] - data['hr_1']
    
    return data

def encode_categorical_variables(data):
    """One-hot encode sleep_score_tier and time_of_day."""
    # One-hot encode sleep_score_tier and time_of_day
    sleep_score_dummies = pd.get_dummies(data['sleep_score_tier'], prefix='sleep_tier')
    time_of_day_dummies = pd.get_dummies(data['time_of_day'], prefix='time')
    
    # Convert to int instead of boolean
    sleep_score_dummies = sleep_score_dummies.astype(int)
    time_of_day_dummies = time_of_day_dummies.astype(int)
    
    # Drop original categorical columns
    data = data.drop(['sleep_score_tier', 'time_of_day'], axis=1)
    
    # Concatenate the one-hot encoded columns
    data = pd.concat([data, sleep_score_dummies, time_of_day_dummies], axis=1)
    
    return data

def create_datasets(data):
    """Create separate datasets for valence and arousal."""
    # Get physiological features
    physiological_cols = ['heart_rate', 'stress', 'respiration', 'body_battery', 'spo2', 'hrv_avg', 'sleep_score', 'hr_change_now', 'hr_change_2min']
    dummy_cols = ['time_Morning', 'time_Afternoon', 'time_Evening', 'time_Night']
    available_cols = [col for col in physiological_cols if col in data.columns]
    available_cols.extend(dummy_cols)
    
    # Print missing values
    print("Missing values: \n", data.isnull().sum())
    
    data = data.dropna()
    
    # Create base features DataFrame
    features = data[['timestamp'] + available_cols].copy()
    
    # Create valence dataset
    valence_data = features.copy()
    valence_data['valence'] = data['valence']
    valence_data = valence_data.dropna(subset=['valence'])
    
    # Create arousal dataset
    arousal_data = features.copy()
    arousal_data['arousal'] = data['arousal']
    arousal_data = arousal_data.dropna(subset=['arousal'])
    
    # Drop specified columns for valence
    valence_columns_to_drop = ['timestamp', 'stress','hrv_avg', 'spo2', 'hr_change_2min', 'time_Afternoon']
    valence_data = valence_data.drop(columns=[col for col in valence_columns_to_drop if col in valence_data.columns])
    
    # Drop specified columns for arousal
    arousal_columns_to_drop = ['stress', 'body_battery', 'sleep_score', 'time_Evening', 'time_Night']
    arousal_data = arousal_data.drop(columns=[col for col in arousal_columns_to_drop if col in arousal_data.columns])
    
    return valence_data, arousal_data

def save_datasets(valence_data, arousal_data, DATA_DIR):
    """Save the processed datasets."""
    # Create new directory if it doesn't exist
    new_dir = os.path.join(DATA_DIR, 'new')
    os.makedirs(new_dir, exist_ok=True)
    
    # Save datasets
    valence_data.to_csv(os.path.join(new_dir, 'final_valence.csv'), index=False)
    arousal_data.to_csv(os.path.join(new_dir, 'final_arousal.csv'), index=False)
    
    print(f"Valence dataset shape: {valence_data.shape}")
    print(f"Arousal dataset shape: {arousal_data.shape}")
    print("Datasets saved successfully!")

def main():
    """Main function to run the feature processing pipeline."""
    # Set up data path
    DATA_DIR = setup_data_path()
    
    # Load data
    cleaned_data, merged_data = load_data(DATA_DIR, 'cleaned_data.csv')
    
    # Add lag features
    data = add_lag_features(cleaned_data, merged_data)
    
    # Encode categorical variables
    data = encode_categorical_variables(data)
    
    # Create datasets
    valence_data, arousal_data = create_datasets(data)
    
    # Save datasets
    save_datasets(valence_data, arousal_data, DATA_DIR)

if __name__ == "__main__":
    main() 