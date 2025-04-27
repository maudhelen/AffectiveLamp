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
    """Load the processed valence and arousal datasets."""
    DATA_DIR = os.path.join(os.getcwd(), 'data', 'new')
    
    valence_data = pd.read_csv(os.path.join(DATA_DIR, 'final_valence.csv'))
    arousal_data = pd.read_csv(os.path.join(DATA_DIR, 'final_arousal.csv'))
    
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
        # 'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
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
    csv_path = os.path.join(plots_dir, f'model_comparison_{target_name}.csv')
    results_df_rounded.to_csv(csv_path, index=False)
    
    # Save as HTML table with styling
    html_path = os.path.join(plots_dir, f'model_comparison_{target_name}.html')
    styled_df = results_df_rounded.style\
        .format({'RMSE': '{:.4f}', 'R2': '{:.4f}', 'CV R2': '{:.4f}'})\
        .background_gradient(subset=['R2', 'CV R2'], cmap='YlGnBu')\
        .background_gradient(subset=['RMSE'], cmap='YlOrRd_r')\
        .set_caption(f'Model Comparison for {target_name.capitalize()} Prediction')\
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
    plt.title(f'Model Comparison for {target_name.capitalize()} Prediction')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f'model_comparison_{target_name}.png'))
    plt.close()
    
    print(f"\nResults saved to {plots_dir}/")
    print(f"- model_comparison_{target_name}.csv")
    print(f"- model_comparison_{target_name}.html")
    print(f"- model_comparison_{target_name}.png")

def get_param_grid(model_name):
    """Return the parameter grid for a given model."""
    param_grids = {
        'Random Forest': {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10]
        },
        'AdaBoost': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 1.0],
            'loss': ['linear', 'square', 'exponential']
        },
        'Gradient Boosting': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 1.0],
            'max_depth': [3, 5, 7]
        },
        'XGBoost': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 1.0],
            'max_depth': [3, 5, 7]
        },
        'LightGBM': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 1.0],
            'max_depth': [3, 5, 7]
        },
        'Decision Tree': {
            'max_depth': [None, 5, 10, 20],
            'min_samples_split': [2, 5, 10]
        },
        'ElasticNet': {
            'alpha': [0.1, 1.0, 10.0],
            'l1_ratio': [0.1, 0.5, 0.9]
        },
        'SVR': {
            'C': [0.1, 1.0, 10.0],
            'kernel': ['linear', 'rbf'],
            'gamma': ['scale', 'auto']
        }
    }
    return param_grids.get(model_name, {})

def tune_best_model(model, X_train, X_test, y_train, y_test, model_name):
    """Perform hyperparameter tuning for the best model."""
    print(f"\nTuning {model_name}...")
    
    # Get parameter grid for the model
    param_grid = get_param_grid(model_name)
    print(f"Parameter grid for {model_name}:")
    for param, values in param_grid.items():
        print(f"  {param}: {values}")
    
    # Create Repeated K-Fold cross-validator
    rkf = RepeatedKFold(n_splits=5, n_repeats=3, random_state=42)
    
    # Perform grid search with repeated k-fold
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=rkf,
        scoring='neg_root_mean_squared_error',
        n_jobs=-1,
        verbose=1
    )
    grid_search.fit(X_train, y_train)
    
    # Print best parameters and score
    print(f"\nBest parameters for {model_name}:")
    for param, value in grid_search.best_params_.items():
        print(f"  {param}: {value}")
    
    # Calculate and print RMSE on test set
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"Test RMSE with best parameters: {rmse:.4f}")
    
    return best_model

def plot_feature_importance(model, feature_names, target_name, model_name):
    """Plot feature importance for models that support it."""
    plots_dir = os.path.join(os.getcwd(), 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Different models have different ways of accessing feature importance
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_)
    else:
        print(f"\nFeature importance not available for {model_name}")
        return
    
    # Create a DataFrame for better visualization
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values('Importance', ascending=False)
    
    # Round importance values to 4 decimal places
    importance_df['Importance'] = importance_df['Importance'].round(4)
    
    # Plot
    plt.figure(figsize=(12, 8))
    sns.barplot(data=importance_df, x='Importance', y='Feature')
    plt.title(f'Feature Importance for {model_name} ({target_name.capitalize()})')
    plt.tight_layout()
    
    # Save plot
    plt.savefig(os.path.join(plots_dir, f'feature_importance_{target_name}_{model_name.replace(" ", "_")}.png'))
    plt.close()
    
    # Save importance values to CSV
    importance_df.to_csv(
        os.path.join(plots_dir, f'feature_importance_{target_name}_{model_name.replace(" ", "_")}.csv'),
        index=False
    )
    
    print(f"Feature importance plot saved to plots/feature_importance_{target_name}_{model_name.replace(' ', '_')}.png")

def main():
    # Load data
    valence_data, arousal_data = load_data()
    
    # Process and evaluate models for valence (always scaled)
    print("\nValence Prediction Models:")
    X_train_v, X_test_v, y_train_v, y_test_v, scaler_v = prepare_data(valence_data, 'valence', always_scale=True)
    results_v, best_model_v = train_models(X_train_v, X_test_v, y_train_v, y_test_v)
    print("\nValence Model Comparison:")
    print(results_v)
    save_results(results_v, 'valence')
    
    # Tune best valence model
    print("\nTuning best valence model:")
    best_model_name_v = results_v.loc[results_v['RMSE'].idxmin(), 'Model']
    best_model_v_tuned = tune_best_model(best_model_v, X_train_v, X_test_v, y_train_v, y_test_v, best_model_name_v)
    
    # Plot feature importance for best valence model
    feature_names = valence_data.drop('valence', axis=1).columns
    plot_feature_importance(best_model_v_tuned, feature_names, 'valence', best_model_name_v)
    
    # Process and evaluate models for arousal (never scaled)
    print("\nArousal Prediction Models:")
    X_train_a, X_test_a, y_train_a, y_test_a, scaler_a = prepare_data(arousal_data, 'arousal', always_scale=True)
    results_a, best_model_a = train_models(X_train_a, X_test_a, y_train_a, y_test_a)
    print("\nArousal Model Comparison:")
    print(results_a)
    save_results(results_a, 'arousal')
    
    # Tune best arousal model
    print("\nTuning best arousal model:")
    best_model_name_a = results_a.loc[results_a['RMSE'].idxmin(), 'Model']
    best_model_a_tuned = tune_best_model(best_model_a, X_train_a, X_test_a, y_train_a, y_test_a, best_model_name_a)
    
    # Plot feature importance for best arousal model
    feature_names = arousal_data.drop('arousal', axis=1).columns
    plot_feature_importance(best_model_a_tuned, feature_names, 'arousal', best_model_name_a)
    
    # Save the best models
    models_dir = os.path.join(os.getcwd(), 'models', 'trained')
    os.makedirs(models_dir, exist_ok=True)
    
    import joblib
    joblib.dump(best_model_v_tuned, os.path.join(models_dir, 'best_valence_model.joblib'))
    joblib.dump(best_model_a_tuned, os.path.join(models_dir, 'best_arousal_model.joblib'))
    if scaler_v is not None:
        joblib.dump(scaler_v, os.path.join(models_dir, 'valence_scaler.joblib'))
    if scaler_a is not None:
        joblib.dump(scaler_a, os.path.join(models_dir, 'arousal_scaler.joblib'))
    
    print("\nBest models have been saved in the models/trained directory.")

if __name__ == "__main__":
    main() 