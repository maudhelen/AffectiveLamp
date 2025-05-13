import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RepeatedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import ElasticNet
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
import os
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    """Load the processed valence and arousal datasets and use only the most recent half of the data."""
    DATA_DIR = os.path.join(os.getcwd(), 'data', 'new')
    
    valence_data = pd.read_csv(os.path.join(DATA_DIR, 'final_valence.csv'))
    arousal_data = pd.read_csv(os.path.join(DATA_DIR, 'final_arousal.csv'))
    
    # Sort by timestamp and take the most recent half
    valence_data = valence_data.tail(len(valence_data) // 2)
    arousal_data = arousal_data.tail(len(arousal_data) // 2)
    
    print(f"Using {len(valence_data)} most recent samples for valence (50% of original)")
    print(f"Using {len(arousal_data)} most recent samples for arousal (50% of original)")
    
    return valence_data, arousal_data

def prepare_data(data, target_col, always_scale=False, never_scale=False):
    """Prepare data for modeling by splitting features and target."""
    X = data.drop([target_col], axis=1)
    y = data[target_col]
    
    # Print some basic statistics about the target variable
    print(f"\nTarget Variable ({target_col}) Statistics:")
    print(f"Mean: {y.mean():.4f}")
    print(f"Std: {y.std():.4f}")
    print(f"Min: {y.min():.4f}")
    print(f"Max: {y.max():.4f}")
    
    # Print correlation with features
    print("\nFeature Correlations with Target:")
    correlations = pd.concat([X, y], axis=1).corr()[target_col].sort_values(ascending=False)
    print(correlations)
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    if always_scale:
        print("\nUsing scaled features (explicitly requested)")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        return X_train_scaled, X_test_scaled, y_train, y_test, scaler
    elif never_scale:
        print("\nUsing unscaled features (explicitly requested)")
        return X_train, X_test, y_train, y_test, None
    else:
        # Try both scaled and unscaled versions
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Use a simple model to test which version performs better
        test_model = RandomForestRegressor(n_estimators=50, random_state=42)
        
        # Test unscaled
        test_model.fit(X_train, y_train)
        unscaled_rmse = np.sqrt(mean_squared_error(y_test, test_model.predict(X_test)))
        
        # Test scaled
        test_model.fit(X_train_scaled, y_train)
        scaled_rmse = np.sqrt(mean_squared_error(y_test, test_model.predict(X_test_scaled)))
        
        print(f"\nScaling Test Results:")
        print(f"Unscaled RMSE: {unscaled_rmse:.4f}")
        print(f"Scaled RMSE: {scaled_rmse:.4f}")
        
        # Choose the better version
        if scaled_rmse < unscaled_rmse:
            print("Using scaled features (better performance)")
            return X_train_scaled, X_test_scaled, y_train, y_test, scaler
        else:
            print("Using unscaled features (better performance)")
            return X_train, X_test, y_train, y_test, None

def evaluate_model(model, X_train, X_test, y_train, y_test, model_name):
    """Train and evaluate a model."""
    print(f"\nEvaluating {model_name}...")
    
    # Create Repeated K-Fold cross-validator
    rkf = RepeatedKFold(n_splits=5, n_repeats=3, random_state=42)
    
    # Train model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Calculate cross-validation scores
    cv_scores = cross_val_score(model, X_train, y_train, 
                              cv=rkf, scoring='neg_root_mean_squared_error')
    cv_rmse = -cv_scores.mean()  # Convert back to positive RMSE
    cv_std = cv_scores.std()
    
    # Calculate baseline metrics
    baseline_pred = np.full_like(y_test, np.mean(y_train))
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))
    
    print(f"RMSE: {rmse:.4f} (Baseline: {baseline_rmse:.4f})")
    print(f"R2 Score: {r2:.4f}")
    print(f"Cross-validation RMSE: {cv_rmse:.4f} (±{cv_std:.4f})")
    
    return model, rmse, r2, cv_rmse

def train_models(X_train, X_test, y_train, y_test):
    """Train and evaluate multiple models."""
    models = {
        'ElasticNet': ElasticNet(random_state=42),
        'SVR': SVR(),
        'Decision Tree': DecisionTreeRegressor(random_state=42),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'AdaBoost': AdaBoostRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=42),
        'LightGBM': LGBMRegressor(n_estimators=100, random_state=42, verbose=-1),        
    }
    
    results = []
    best_model = None
    best_r2 = -float('inf')
    
    for name, model in models.items():
        model, rmse, r2, cv_r2 = evaluate_model(model, X_train, X_test, y_train, y_test, name)
        results.append({
            'Model': name,
            'RMSE': rmse,
            'R2': r2,
            'CV R2': cv_r2
        })
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
    
    return pd.DataFrame(results), best_model

def save_results(results_df, target_name):
    """Save model comparison results as CSV and HTML tables."""
    plots_dir = os.path.join(os.getcwd(), 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Round numerical columns to 4 decimal places
    results_df_rounded = results_df.copy()
    for col in ['RMSE', 'R2', 'CV R2']:
        if col in results_df_rounded.columns:
            results_df_rounded[col] = results_df_rounded[col].round(4)
    
    # Save as CSV
    csv_path = os.path.join(plots_dir, f'model_comparison_{target_name}_newest_half.csv')
    results_df_rounded.to_csv(csv_path, index=False)
    
    # Save as HTML table with styling
    html_path = os.path.join(plots_dir, f'model_comparison_{target_name}_newest_half.html')
    styled_df = results_df_rounded.style\
        .format({'RMSE': '{:.4f}', 'R2': '{:.4f}', 'CV R2': '{:.4f}'})\
        .background_gradient(subset=['R2', 'CV R2'], cmap='YlGnBu')\
        .background_gradient(subset=['RMSE'], cmap='YlOrRd_r')\
        .set_caption(f'Model Comparison for {target_name.capitalize()} Prediction (Newest Half Data)')\
        .set_table_styles([
            {'selector': 'caption',
             'props': [('font-size', '16px'),
                      ('font-weight', 'bold'),
                      ('text-align', 'center'),
                      ('margin-bottom', '10px')]},
            {'selector': 'th',
             'props': [('background-color', '#f8f9fa'),
                      ('font-weight', 'bold'),
                      ('text-align', 'center')]},
            {'selector': 'td',
             'props': [('text-align', 'center')]}
        ])
    
    with open(html_path, 'w') as f:
        f.write(styled_df.to_html())
    
    # Create and save bar plot
    plt.figure(figsize=(12, 6))
    sns.barplot(data=results_df, x='Model', y='R2')
    plt.title(f'Model Comparison for {target_name.capitalize()} Prediction (Newest Half Data)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f'model_comparison_{target_name}_newest_half.png'))
    plt.close()
    
    print(f"\nResults saved to {plots_dir}/")
    print(f"- model_comparison_{target_name}_newest_half.csv")
    print(f"- model_comparison_{target_name}_newest_half.html")
    print(f"- model_comparison_{target_name}_newest_half.png")

def main():
    # Load data
    valence_data, arousal_data = load_data()
    
    # Process and evaluate models for valence (always scaled)
    print("\nValence Prediction Models (Newest Half Data):")
    X_train_v, X_test_v, y_train_v, y_test_v, scaler_v = prepare_data(valence_data, 'valence', always_scale=True)
    results_v, best_model_v = train_models(X_train_v, X_test_v, y_train_v, y_test_v)
    print("\nValence Model Comparison (Newest Half Data):")
    print(results_v)
    save_results(results_v, 'valence')
    
    # Process and evaluate models for arousal (never scaled)
    print("\nArousal Prediction Models (Newest Half Data):")
    X_train_a, X_test_a, y_train_a, y_test_a, scaler_a = prepare_data(arousal_data, 'arousal', always_scale=True)
    results_a, best_model_a = train_models(X_train_a, X_test_a, y_train_a, y_test_a)
    print("\nArousal Model Comparison (Newest Half Data):")
    print(results_a)
    save_results(results_a, 'arousal')
    
    # Save the best models
    models_dir = os.path.join(os.getcwd(), 'models', 'trained')
    os.makedirs(models_dir, exist_ok=True)
    
    import joblib
    joblib.dump(best_model_v, os.path.join(models_dir, 'best_valence_model_newest_half.joblib'))
    joblib.dump(best_model_a, os.path.join(models_dir, 'best_arousal_model_newest_half.joblib'))
    if scaler_v is not None:
        joblib.dump(scaler_v, os.path.join(models_dir, 'valence_scaler_newest_half.joblib'))
    if scaler_a is not None:
        joblib.dump(scaler_a, os.path.join(models_dir, 'arousal_scaler_newest_half.joblib'))
    
    print("\nBest models have been saved in the models/trained directory with '_newest_half' suffix.")

if __name__ == "__main__":
    main() 