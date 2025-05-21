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

def load_data(seed=100):
    """Load the processed valence and arousal datasets and use only half of the data."""
    DATA_DIR = os.path.join(os.getcwd(), 'data', 'new')
    
    valence_data = pd.read_csv(os.path.join(DATA_DIR, 'final_valence.csv'))
    arousal_data = pd.read_csv(os.path.join(DATA_DIR, 'final_arousal.csv'))
    
    valence_data = valence_data.sample(frac=0.5, random_state=seed)
    arousal_data = arousal_data.sample(frac=0.5, random_state=seed)
    
    print(f"[Seed {seed}] Using {len(valence_data)} valence samples")
    print(f"[Seed {seed}] Using {len(arousal_data)} arousal samples")
    
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
    
    # Always use unscaled features for half data experiments
    print("\nUsing unscaled features for half data experiment")
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
        model, rmse, r2, cv_rmse = evaluate_model(model, X_train, X_test, y_train, y_test, name)
        results.append({
            'Model': name,
            'RMSE': rmse,
            # 'CV RMSE': cv_rmse,
            'R2': r2,
        })
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
    
    return pd.DataFrame(results), best_model

def save_results(results_df, target_name):
    """Save model comparison results as CSV and HTML tables."""
    plots_dir = os.path.join(os.getcwd(), 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Read the full dataset results
    full_data_path = os.path.join(plots_dir, f'model_comparison_{target_name}_no_scaling.csv')
    if os.path.exists(full_data_path):
        full_data_results = pd.read_csv(full_data_path)
        
        # Calculate RMSE improvement percentage
        results_df['RMSE Improvement %'] = ((full_data_results['RMSE'] - results_df['RMSE']) / full_data_results['RMSE'] * 100).round(2)
        
        # Add full dataset RMSE for reference
        results_df['Full Dataset RMSE'] = full_data_results['RMSE'].round(4)
    
    # Round numerical columns to 4 decimal places
    results_df_rounded = results_df.copy()
    for col in ['RMSE', 'R2', 'CV RMSE']:
        if col in results_df_rounded.columns:
            results_df_rounded[col] = results_df_rounded[col].round(4)
    
    # Save as CSV
    csv_path = os.path.join(plots_dir, f'model_comparison_{target_name}_half_data.csv')
    results_df_rounded.to_csv(csv_path, index=False)
    
    # Create and save bar plot
    plt.figure(figsize=(12, 6))
    sns.barplot(data=results_df, x='Model', y='R2')
    plt.title(f'Model Comparison for {target_name.capitalize()} Prediction (Half Data)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f'model_comparison_{target_name}_half_data.png'))
    plt.close()
    
    print(f"\nResults saved to {plots_dir}/")
    print(f"- model_comparison_{target_name}_half_data.csv")
    print(f"- model_comparison_{target_name}_half_data.html")
    print(f"- model_comparison_{target_name}_half_data.png")

def main():
    SEEDS = [42, 99, 7, 123, 2024]
    all_results_v = []
    all_results_a = []
    
    plots_dir = os.path.join(os.getcwd(), 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    for seed in SEEDS:
        print(f"\n=== Running models for seed {seed} ===")

        # Load sampled data
        valence_data, arousal_data = load_data(seed=seed)

        # Valence
        print("\nValence Prediction:")
        X_train_v, X_test_v, y_train_v, y_test_v, _ = prepare_data(valence_data, 'valence', never_scale=True)
        results_v, _ = train_models(X_train_v, X_test_v, y_train_v, y_test_v)
        results_v['Seed'] = seed
        all_results_v.append(results_v)

        # Arousal
        print("\nArousal Prediction:")
        X_train_a, X_test_a, y_train_a, y_test_a, _ = prepare_data(arousal_data, 'arousal', never_scale=True)
        results_a, _ = train_models(X_train_a, X_test_a, y_train_a, y_test_a)
        results_a['Seed'] = seed
        all_results_a.append(results_a)

    # Combine and average
    combined_v = pd.concat(all_results_v)
    combined_a = pd.concat(all_results_a)

    # Average across seeds
    avg_results_v = combined_v.groupby("Model").agg({
        "RMSE": "mean"
    }).rename(columns={"RMSE": "RMSE Half Data"}).round(4)

    avg_results_a = combined_a.groupby("Model").agg({
        "RMSE": "mean"
    }).rename(columns={"RMSE": "RMSE Half Data"}).round(4)

    # Load full dataset RMSEs
    full_valence_path = os.path.join(plots_dir, 'model_comparison_valence.csv')
    full_arousal_path = os.path.join(plots_dir, 'model_comparison_arousal.csv')

    full_v = pd.read_csv(full_valence_path)[['Model', 'RMSE']].set_index("Model")
    full_v = full_v.rename(columns={"RMSE": "RMSE Full Data"})

    full_a = pd.read_csv(full_arousal_path)[['Model', 'RMSE']].set_index("Model")
    full_a = full_a.rename(columns={"RMSE": "RMSE Full Data"})

    # Merge and compute improvement
    merged_v = avg_results_v.join(full_v, how="inner")
    merged_a = avg_results_a.join(full_a, how="inner")

    merged_v["% RMSE Improvement"] = ((merged_v["RMSE Full Data"] - merged_v["RMSE Half Data"]) / merged_v["RMSE Full Data"] * 100).round(2)
    merged_a["% RMSE Improvement"] = ((merged_a["RMSE Full Data"] - merged_a["RMSE Half Data"]) / merged_a["RMSE Full Data"] * 100).round(2)

    # Save final comparison tables
    merged_v.to_csv(os.path.join(plots_dir, 'final_valence_rmse_comparison.csv'))
    merged_a.to_csv(os.path.join(plots_dir, 'final_arousal_rmse_comparison.csv'))

    print("\n📊 Final RMSE comparison tables saved:")
    print("- final_valence_rmse_comparison.csv")
    print("- final_arousal_rmse_comparison.csv")

if __name__ == "__main__":
    main() 