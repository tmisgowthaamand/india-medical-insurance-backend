# app.py
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from joblib import load, dump
import pandas as pd
import os
import json
import numpy as np
from datetime import datetime

from model_pipeline import build_pipeline, get_feature_importance
from utils import hash_password, verify_password, create_access_token, decode_token, get_current_user

app = FastAPI(title="India Medical Insurance ML Dashboard", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configuration
MODEL_PATH = "models/model_pipeline.pkl"
USERS_DB = "users.json"
CSV_PATH = "data/sample_medical_insurance_data.csv"

# Global variables
model = None

# Ensure we have a dataset on startup
def ensure_dataset_exists():
    """Ensure at least one dataset file exists"""
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')] if os.path.exists(data_dir) else []
    
    if not csv_files:
        print("No dataset found. Creating sample dataset...")
        from create_sample_data import create_sample_dataset
        create_sample_dataset()

# Ensure dataset exists
ensure_dataset_exists()

# Load model on startup if exists
if os.path.exists(MODEL_PATH):
    try:
        model = load(MODEL_PATH)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print("No model found. Please train a model first.")

# Pydantic models
class UserIn(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    email: str
    created_at: str

class PredictIn(BaseModel):
    age: int
    bmi: float
    gender: str
    smoker: str
    region: str
    premium_annual_inr: Optional[float] = None

class PredictResponse(BaseModel):
    predicted_claim: float
    confidence: float
    input_data: dict

class StatsResponse(BaseModel):
    total_policies: int
    avg_premium: float
    avg_claim: float
    avg_age: float
    avg_bmi: float
    smoker_percentage: float
    regions: dict
    genders: dict

class ClaimsAnalysis(BaseModel):
    age_groups: dict
    region_analysis: dict
    smoker_analysis: dict
    premium_vs_claims: List[dict]

# Utility functions
def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_DB, 'w') as f:
        json.dump(users, f, indent=2)

def get_current_user_from_token(authorization: str = Depends(get_current_user)):
    """Get current user from JWT token"""
    return authorization

# Routes
@app.get("/")
def root():
    return {"message": "India Medical Insurance ML Dashboard API", "version": "1.0.0"}

@app.options("/{path:path}")
def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return {"message": "OK"}

@app.post('/signup', response_model=dict)
def signup(payload: UserIn):
    """Register a new user"""
    users = load_users()
    
    if payload.email in users:
        raise HTTPException(status_code=400, detail='Email already exists')
    
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail='Password must be at least 6 characters')
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, payload.email):
        raise HTTPException(status_code=400, detail='Invalid email format')
    
    # For demo purposes, store password in plain text (NOT for production!)
    users[payload.email] = {
        "password": payload.password[:72],
        "created_at": datetime.now().isoformat(),
        "is_admin": payload.email == "admin@example.com"
    }
    
    save_users(users)
    return {"message": "User created successfully", "email": payload.email}

@app.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token"""
    print(f"Login attempt for: {form_data.username}")
    
    users = load_users()
    
    if not users:
        default_users = {
            "admin@example.com": {
                "password": "admin123",
                "created_at": datetime.now().isoformat(),
                "is_admin": True
            },
            "user@example.com": {
                "password": "user123",
                "created_at": datetime.now().isoformat(),
                "is_admin": False
            },
            "demo@example.com": {
                "password": "demo123",
                "created_at": datetime.now().isoformat(),
                "is_admin": False
            }
        }
        save_users(default_users)
        users = default_users
    
    user = users.get(form_data.username)
    if not user:
        print(f"User not found: {form_data.username}")
        raise HTTPException(status_code=401, detail='Invalid email or password')
    
    # Simple password comparison for demo
    password_valid = (form_data.password == user['password'])
    
    if not password_valid:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    
    token = create_access_token({"sub": form_data.username, "is_admin": user.get("is_admin", False)})
    return {
        "access_token": token, 
        "token_type": "bearer",
        "email": form_data.username,
        "is_admin": user.get("is_admin", False)
    }

@app.get('/me')
def get_current_user_info(current_user: str = Depends(get_current_user_from_token)):
    """Get current user information"""
    users = load_users()
    user = users.get(current_user, {})
    return {
        "email": current_user,
        "created_at": user.get("created_at"),
        "is_admin": user.get("is_admin", False)
    }

@app.post('/predict', response_model=PredictResponse)
def predict(payload: PredictIn, current_user: str = Depends(get_current_user_from_token)):
    """Make insurance claim prediction"""
    if model is None:
        raise HTTPException(status_code=503, detail='Model not loaded. Please train the model first.')
    
    # Prepare input data
    input_data = {
        'age': payload.age,
        'bmi': payload.bmi,
        'gender': payload.gender,
        'smoker': payload.smoker,
        'region': payload.region,
        'premium_annual_inr': payload.premium_annual_inr or 25000
    }
    
    try:
        # Create DataFrame for prediction
        df = pd.DataFrame([input_data])
        
        # Make prediction
        prediction = model.predict(df)[0]
        
        # Calculate confidence (simplified)
        confidence = min(0.95, max(0.7, 1.0 - abs(prediction - 25000) / 50000))
        
        return PredictResponse(
            predicted_claim=float(prediction),
            confidence=confidence,
            input_data=input_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get('/stats', response_model=StatsResponse)
def get_stats():
    """Get dataset statistics"""
    # Find an available dataset file
    dataset_to_use = None
    
    if os.path.exists(CSV_PATH):
        dataset_to_use = CSV_PATH
    else:
        data_dir = "data"
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith('.csv'):
                    dataset_to_use = os.path.join(data_dir, file)
                    break
    
    if not dataset_to_use:
        raise HTTPException(status_code=404, detail='No dataset found. Please upload a dataset first.')
    
    try:
        df = pd.read_csv(dataset_to_use)
        
        stats = StatsResponse(
            total_policies=int(len(df)),
            avg_premium=float(df['premium_annual_inr'].mean()),
            avg_claim=float(df['claim_amount_inr'].mean()),
            avg_age=float(df['age'].mean()),
            avg_bmi=float(df['bmi'].mean()),
            smoker_percentage=float((df['smoker'] == 'Yes').mean() * 100),
            regions=df['region'].value_counts().to_dict(),
            genders=df['gender'].value_counts().to_dict()
        )
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")

@app.get('/claims-analysis', response_model=ClaimsAnalysis)
def get_claims_analysis():
    """Get detailed claims analysis"""
    # Find an available dataset file
    dataset_to_use = None
    
    if os.path.exists(CSV_PATH):
        dataset_to_use = CSV_PATH
    else:
        data_dir = "data"
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith('.csv'):
                    dataset_to_use = os.path.join(data_dir, file)
                    break
    
    if not dataset_to_use:
        raise HTTPException(status_code=404, detail='No dataset found. Please upload a dataset first.')
    
    try:
        df = pd.read_csv(dataset_to_use)
        
        # Age group analysis
        df['age_group'] = pd.cut(df['age'], bins=[0, 30, 40, 50, 60, 100], labels=['<30', '30-40', '40-50', '50-60', '60+'])
        age_groups = df.groupby('age_group').agg({
            'claim_amount_inr': 'mean',
            'premium_annual_inr': 'mean'
        }).to_dict()
        
        # Region analysis
        region_analysis = df.groupby('region').agg({
            'claim_amount_inr': ['mean', 'count'],
            'premium_annual_inr': 'mean'
        }).to_dict()
        
        # Smoker analysis
        smoker_analysis = df.groupby('smoker').agg({
            'claim_amount_inr': ['mean', 'count'],
            'premium_annual_inr': 'mean'
        }).to_dict()
        
        # Premium vs Claims correlation
        premium_vs_claims = df[['premium_annual_inr', 'claim_amount_inr']].to_dict('records')
        
        return ClaimsAnalysis(
            age_groups=age_groups,
            region_analysis=region_analysis,
            smoker_analysis=smoker_analysis,
            premium_vs_claims=premium_vs_claims[:100]  # Limit to 100 points
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in claims analysis: {str(e)}")

@app.get('/model-info')
def get_model_info(current_user: str = Depends(get_current_user_from_token)):
    """Get model information and feature importance"""
    if model is None:
        return {"status": "No model loaded"}
    
    info = {"status": "Model loaded"}
    
    # Load training metadata if available
    metadata_path = "models/training_metadata.json"
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            info.update(metadata)
    
    return info

@app.post('/admin/upload')
def admin_upload(file: UploadFile = File(...), current_user: str = Depends(get_current_user_from_token)):
    """Upload dataset and retrain model (Admin only)"""
    # Check if user is admin
    users = load_users()
    user = users.get(current_user, {})
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Save uploaded file
        os.makedirs("data", exist_ok=True)
        file_path = f"data/{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Validate CSV structure
        try:
            df = pd.read_csv(file_path)
            required_columns = ['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr', 'claim_amount_inr']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}")
        
        except pd.errors.EmptyDataError:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        except Exception as e:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")
        
        # Retrain model with the uploaded dataset
        from train import train
        try:
            new_model = train(dataset_path=file_path)
            if new_model:
                global model, CSV_PATH
                model = new_model
                CSV_PATH = file_path
                return {"message": f"File uploaded successfully and model retrained. Dataset has {len(df)} rows."}
            else:
                return {"message": "File uploaded but model training failed"}
        except Exception as e:
            return {"message": f"File uploaded but model training failed: {str(e)}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post('/admin/retrain')
def admin_retrain(current_user: str = Depends(get_current_user_from_token)):
    """Retrain model with existing dataset (Admin only)"""
    # Check if user is admin
    users = load_users()
    user = users.get(current_user, {})
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Find available dataset files
        data_dir = "data"
        available_files = []
        
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith('.csv'):
                    available_files.append(os.path.join(data_dir, file))
        
        if not available_files:
            raise HTTPException(status_code=404, detail="No dataset files found. Please upload a dataset first.")
        
        # Use the most recent CSV file or the current CSV_PATH if it exists
        dataset_to_use = CSV_PATH if os.path.exists(CSV_PATH) else available_files[0]
        
        from train import train
        new_model = train(dataset_path=dataset_to_use)
        if new_model:
            global model, CSV_PATH
            model = new_model
            CSV_PATH = dataset_to_use
            return {"message": f"Model retrained successfully using {os.path.basename(dataset_to_use)}"}
        else:
            raise HTTPException(status_code=500, detail="Model training failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
