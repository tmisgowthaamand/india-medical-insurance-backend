# model_pipeline.py
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor

NUMERIC_FEATURES = ["age", "bmi", "premium_annual_inr"]
CATEGORICAL_FEATURES = ["gender", "smoker", "region"]


def build_pipeline(random_state=42):
    """Build the ML pipeline with preprocessing and RandomForestRegressor"""
    numeric_pipe = Pipeline([
        ("scaler", StandardScaler())
    ])

    cat_pipe = Pipeline([
        ("ohe", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_pipe, NUMERIC_FEATURES),
        ("cat", cat_pipe, CATEGORICAL_FEATURES)
    ])

    model = RandomForestRegressor(
        n_estimators=200, 
        random_state=random_state,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        criterion='squared_error'  # Use compatible criterion
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", model)
    ])

    return pipeline


def get_feature_importance(pipeline, feature_names=None):
    """Get feature importance from trained pipeline"""
    if feature_names is None:
        feature_names = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    
    if hasattr(pipeline.named_steps['regressor'], 'feature_importances_'):
        importances = pipeline.named_steps['regressor'].feature_importances_
        
        # Get feature names after preprocessing
        preprocessor = pipeline.named_steps['preprocessor']
        feature_names_transformed = []
        
        # Add numeric features
        feature_names_transformed.extend(NUMERIC_FEATURES)
        
        # Add categorical features (one-hot encoded)
        if hasattr(preprocessor.named_transformers_['cat'], 'named_steps'):
            ohe = preprocessor.named_transformers_['cat'].named_steps['ohe']
            if hasattr(ohe, 'get_feature_names_out'):
                cat_features = ohe.get_feature_names_out(CATEGORICAL_FEATURES)
                feature_names_transformed.extend(cat_features)
        
        return dict(zip(feature_names_transformed[:len(importances)], importances))
    
    return {}
