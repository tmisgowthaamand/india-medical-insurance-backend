# fast_train.py - Optimized for speed
import pandas as pd
import os
import time
from joblib import dump
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from fast_model_pipeline import build_fast_pipeline, get_model_info
import numpy as np

CSV_PATH = "data/sample_medical_insurance_data.csv"
MODEL_OUT = "models/model_pipeline.pkl"


def fast_train(dataset_path=None, model_type="fast_rf"):
    """Fast model training optimized for speed"""
    start_time = time.time()
    print("🚀 Starting FAST model training...")
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Use provided dataset path or default
    data_path = dataset_path if dataset_path else CSV_PATH
    data_path = os.path.normpath(data_path)
    print(f"📊 Using dataset: {os.path.basename(data_path)}")
    
    # Load data
    if not os.path.exists(data_path):
        print(f"❌ Dataset not found at {data_path}")
        return None
    
    df = pd.read_csv(data_path)
    print(f"📈 Loaded {len(df)} rows")
    
    # Quick data cleaning (optimized)
    print("🧹 Quick data cleaning...")
    
    # Remove rows with missing target
    df = df.dropna(subset=["claim_amount_inr"])
    
    # Fast missing value handling
    numeric_cols = ['age', 'bmi', 'premium_annual_inr']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    categorical_cols = ['gender', 'smoker', 'region']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
    
    print(f"✅ Cleaned data: {len(df)} rows")
    
    # Prepare features and target
    feature_columns = ["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"]
    X = df[feature_columns]
    y = df["claim_amount_inr"]
    
    # Quick data split (smaller test size for faster training)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42  # Reduced from 0.2 to 0.15
    )
    
    print(f"🔄 Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Build and train fast pipeline
    print(f"⚡ Training {model_type} model...")
    training_start = time.time()
    
    pipeline = build_fast_pipeline(model_type=model_type)
    pipeline.fit(X_train, y_train)
    
    training_time = time.time() - training_start
    print(f"✅ Training completed in {training_time:.2f} seconds")
    
    # Quick evaluation
    print("📊 Evaluating model...")
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)
    
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    print(f"\n📈 Model Performance:")
    print(f"   Training RMSE: ₹{train_rmse:.2f}")
    print(f"   Test RMSE: ₹{test_rmse:.2f}")
    print(f"   Training R²: {train_r2:.4f}")
    print(f"   Test R²: {test_r2:.4f}")
    
    # Save model
    dump(pipeline, MODEL_OUT)
    print(f"💾 Model saved to {MODEL_OUT}")
    
    # Save training metadata
    total_time = time.time() - start_time
    metadata = {
        'training_date': pd.Timestamp.now().isoformat(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'train_rmse': float(train_rmse),
        'test_rmse': float(test_rmse),
        'train_r2': float(train_r2),
        'test_r2': float(test_r2),
        'features': feature_columns,
        'model_type': model_type,
        'training_time_seconds': round(training_time, 2),
        'total_time_seconds': round(total_time, 2),
        'optimized_for': 'speed'
    }
    
    # Add model-specific info
    model_info = get_model_info(pipeline)
    metadata.update(model_info)
    
    import json
    with open('models/training_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"🎉 FAST training completed in {total_time:.2f} seconds total!")
    return pipeline


def train(dataset_path=None):
    """Default train function - now uses fast training"""
    return fast_train(dataset_path, model_type="fast_rf")


if __name__ == "__main__":
    # Test different model types
    print("Testing different model speeds:")
    
    print("\n1. Fastest (Linear Regression):")
    fast_train(model_type="fastest")
    
    print("\n2. Fast Tree (Decision Tree):")
    fast_train(model_type="fast_tree")
    
    print("\n3. Fast RF (Optimized Random Forest):")
    fast_train(model_type="fast_rf")
