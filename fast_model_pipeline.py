# fast_model_pipeline.py - Optimized for speed
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
import numpy as np

NUMERIC_FEATURES = ["age", "bmi", "premium_annual_inr"]
CATEGORICAL_FEATURES = ["gender", "smoker", "region"]


def build_fast_pipeline(model_type="fast_rf", random_state=42):
    """Build optimized ML pipeline for fast training"""
    
    # Simplified preprocessing for speed
    numeric_pipe = Pipeline([
        ("scaler", StandardScaler())
    ])

    cat_pipe = Pipeline([
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_pipe, NUMERIC_FEATURES),
        ("cat", cat_pipe, CATEGORICAL_FEATURES)
    ])

    # Choose model based on type for different speed/accuracy tradeoffs
    if model_type == "fastest":
        # Linear regression - fastest training
        model = LinearRegression()
    elif model_type == "fast_tree":
        # Single decision tree - very fast (compatible parameters)
        model = DecisionTreeRegressor(
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=random_state,
            splitter='best',
            criterion='squared_error'  # Use compatible criterion
        )
    elif model_type == "fast_rf":
        # Optimized Random Forest - balanced speed/accuracy
        model = RandomForestRegressor(
            n_estimators=50,  # Reduced from 200 to 50
            max_depth=8,      # Reduced from 10 to 8
            min_samples_split=10,  # Increased from 5 to 10
            min_samples_leaf=5,    # Increased from 2 to 5
            n_jobs=-1,        # Use all CPU cores
            random_state=random_state,
            bootstrap=True,
            max_features='sqrt',  # Use sqrt of features for speed
            criterion='squared_error'  # Use compatible criterion
        )
    else:
        # Default to fast RF
        model = RandomForestRegressor(
            n_estimators=50,
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            n_jobs=-1,
            random_state=random_state,
            criterion='squared_error'  # Use compatible criterion
        )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", model)
    ])

    return pipeline


def build_pipeline(random_state=42):
    """Default pipeline - now uses fast version"""
    return build_fast_pipeline("fast_rf", random_state)


def get_feature_importance(pipeline, feature_names=None):
    """Get feature importance from trained pipeline"""
    if feature_names is None:
        feature_names = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    
    regressor = pipeline.named_steps['regressor']
    
    # Handle different model types
    if hasattr(regressor, 'feature_importances_'):
        importances = regressor.feature_importances_
        
        # Get feature names after preprocessing
        preprocessor = pipeline.named_steps['preprocessor']
        feature_names_transformed = []
        
        # Add numeric features
        feature_names_transformed.extend(NUMERIC_FEATURES)
        
        # Add categorical features (one-hot encoded)
        try:
            cat_transformer = preprocessor.named_transformers_['cat']
            if hasattr(cat_transformer, 'named_steps'):
                ohe = cat_transformer.named_steps['ohe']
                if hasattr(ohe, 'get_feature_names_out'):
                    cat_features = ohe.get_feature_names_out(CATEGORICAL_FEATURES)
                    feature_names_transformed.extend(cat_features)
        except:
            # Fallback for categorical features
            feature_names_transformed.extend(['gender_encoded', 'smoker_encoded', 'region_encoded'])
        
        # Ensure we don't exceed the number of importances
        min_len = min(len(importances), len(feature_names_transformed))
        return dict(zip(feature_names_transformed[:min_len], importances[:min_len]))
    
    elif hasattr(regressor, 'coef_'):
        # For linear models
        coefficients = regressor.coef_
        feature_names_transformed = NUMERIC_FEATURES + ['gender_encoded', 'smoker_encoded', 'region_encoded']
        min_len = min(len(coefficients), len(feature_names_transformed))
        return dict(zip(feature_names_transformed[:min_len], coefficients[:min_len]))
    
    return {}


def get_model_info(pipeline):
    """Get information about the trained model"""
    regressor = pipeline.named_steps['regressor']
    
    info = {
        "model_type": type(regressor).__name__,
        "training_time": "Fast (< 30 seconds)",
        "optimized_for": "Speed"
    }
    
    if hasattr(regressor, 'n_estimators'):
        info["n_estimators"] = regressor.n_estimators
    if hasattr(regressor, 'max_depth'):
        info["max_depth"] = regressor.max_depth
    if hasattr(regressor, 'n_jobs'):
        info["n_jobs"] = regressor.n_jobs
        
    return info
