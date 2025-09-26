# train.py
import pandas as pd
import os
from joblib import dump
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from model_pipeline import build_pipeline
import numpy as np

CSV_PATH = "data/sample_medical_insurance_data.csv"
MODEL_OUT = "models/model_pipeline.pkl"


def train(dataset_path=None):
    """Train the ML model and save it"""
    print("Starting model training...")
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Use provided dataset path or default
    data_path = dataset_path if dataset_path else CSV_PATH
    
    # Normalize the path to handle different path separators
    data_path = os.path.normpath(data_path)
    print(f"Using dataset path: {data_path}")
    
    # Load data
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in data directory:")
        data_dir = os.path.dirname(data_path)
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                print(f"  - {file}")
        else:
            print(f"  Data directory {data_dir} does not exist")
        print("Please ensure the dataset file exists")
        return None
    
    df = pd.read_csv(data_path)
    print(f"Loaded dataset with {len(df)} rows")
    
    # Basic data cleaning
    print("Cleaning data...")
    initial_rows = len(df)
    
    # Remove rows with missing target variable
    df = df.dropna(subset=["claim_amount_inr"])
    
    # Handle missing values in features
    df['age'] = df['age'].fillna(df['age'].median())
    df['bmi'] = df['bmi'].fillna(df['bmi'].median())
    df['premium_annual_inr'] = df['premium_annual_inr'].fillna(df['premium_annual_inr'].median())
    
    # Fill categorical missing values
    df['gender'] = df['gender'].fillna('Unknown')
    df['smoker'] = df['smoker'].fillna('Unknown')
    df['region'] = df['region'].fillna('Unknown')
    
    print(f"After cleaning: {len(df)} rows (removed {initial_rows - len(df)} rows)")
    
    # Prepare features and target
    feature_columns = ["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"]
    X = df[feature_columns]
    y = df["claim_amount_inr"]
    
    print(f"Features: {feature_columns}")
    print(f"Target: claim_amount_inr")
    print(f"Target statistics:")
    print(f"  Mean: ₹{y.mean():.2f}")
    print(f"  Median: ₹{y.median():.2f}")
    print(f"  Std: ₹{y.std():.2f}")
    print(f"  Min: ₹{y.min():.2f}")
    print(f"  Max: ₹{y.max():.2f}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Build and train pipeline
    print("Training model...")
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    
    # Evaluate model
    print("Evaluating model...")
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)
    
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    print(f"\nModel Performance:")
    print(f"Training RMSE: ₹{train_rmse:.2f}")
    print(f"Test RMSE: ₹{test_rmse:.2f}")
    print(f"Training R²: {train_r2:.4f}")
    print(f"Test R²: {test_r2:.4f}")
    
    # Save model
    dump(pipeline, MODEL_OUT)
    print(f"\nModel saved to {MODEL_OUT}")
    
    # Save training metadata
    metadata = {
        'training_date': pd.Timestamp.now().isoformat(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'train_rmse': float(train_rmse),
        'test_rmse': float(test_rmse),
        'train_r2': float(train_r2),
        'test_r2': float(test_r2),
        'features': feature_columns
    }
    
    import json
    with open('models/training_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("Training completed successfully!")
    return pipeline


if __name__ == "__main__":
    train()
