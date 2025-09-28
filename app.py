# app.py
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header
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
import asyncio

from model_pipeline import build_pipeline, get_feature_importance
from utils import hash_password, verify_password, create_access_token, decode_token, get_current_user
from database import supabase_client, init_database
from error_handler import setup_error_handlers, log_startup_info, request_logging_middleware

app = FastAPI(title="India Medical Insurance ML Dashboard", version="1.0.0")

# Setup error handling
setup_error_handlers(app)

# Add request logging middleware
app.middleware("http")(request_logging_middleware)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and load model on startup"""
    log_startup_info()
    print("Starting up application...")
    
    try:
        # Initialize database
        await init_database()
        print("✅ Database initialization completed")
        
        # Load model if exists
        global model
        if os.path.exists(MODEL_PATH):
            try:
                model = load(MODEL_PATH)
                print("✅ Model loaded successfully")
            except Exception as e:
                print(f"⚠️ Error loading model: {e}")
                model = None
        else:
            print("⚠️ No model found. Please train a model first.")
            model = None
            
        print("🚀 Application startup completed successfully")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        # Don't raise the exception to allow the server to start

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down application...")

# CORS middleware
# Get allowed origins from environment variable or use default for development
import os
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "https://india-medical-insurance-frontend.vercel.app,http://localhost:3000,http://localhost:3001,*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

print(f"CORS allowed origins: {allowed_origins}")  # Debug log

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=[
        "*",
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
    expose_headers=[
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers"
    ]
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
    prediction: float
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
    gender_distribution: dict

class ClaimsAnalysis(BaseModel):
    age_groups: dict
    region_analysis: dict
    smoker_analysis: dict
    premium_vs_claims: dict

# Helper functions
def get_current_user_from_token(authorization: str = Header(None)):
    """Extract user from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        username = get_current_user(token)
        return username
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

async def load_users():
    """Load users from Supabase or fallback to JSON file"""
    if supabase_client.is_enabled():
        try:
            users_data = await supabase_client.get_all_users()
            # Convert to the format expected by the rest of the code
            users = {}
            for user in users_data:
                users[user['email']] = {
                    'password': user.get('password', ''),
                    'created_at': user.get('created_at', ''),
                    'is_admin': user.get('is_admin', False)
                }
            return users
        except Exception as e:
            print(f"Error loading users from Supabase: {e}")
    
    # Fallback to JSON file
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r') as f:
            return json.load(f)
    return {}

async def save_users(users):
    """Save users to Supabase or fallback to JSON file"""
    if supabase_client.is_enabled():
        try:
            # Note: In a real application, you'd want to handle updates vs inserts
            # For now, we'll just log that this should be handled differently
            print("User management through Supabase should use individual user operations")
            return
        except Exception as e:
            print(f"Error saving users to Supabase: {e}")
    
    # Fallback to JSON file
    with open(USERS_DB, 'w') as f:
        json.dump(users, f, indent=2)

# Routes
@app.get("/")
@app.head("/")
def root():
    return {"message": "India Medical Insurance ML Dashboard API", "version": "1.0.0"}

@app.get("/health")
@app.head("/health")
def health_check():
    """Health check endpoint for deployment platforms"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "model_loaded": model is not None,
        "cors_origins": allowed_origins
    }

@app.get("/cors-test")
def cors_test():
    """CORS test endpoint"""
    return {
        "message": "CORS test successful",
        "allowed_origins": allowed_origins,
        "timestamp": datetime.now().isoformat()
    }

@app.options("/{path:path}")
def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return {"message": "OK"}

@app.head("/{path:path}")
def head_handler(path: str):
    """Handle HEAD requests for health checks and monitoring"""
    # HEAD requests should return empty body with proper status
    return {}

@app.post('/signup', response_model=dict)
async def signup(payload: UserIn):
    """Register a new user"""
    # Try Supabase first
    if supabase_client.is_enabled():
        try:
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, payload.email):
                raise HTTPException(status_code=400, detail='Invalid email format')
            
            if len(payload.password) < 6:
                raise HTTPException(status_code=400, detail='Password must be at least 6 characters')
            
            # Check if user already exists
            existing_user = await supabase_client.get_user(payload.email)
            if existing_user:
                raise HTTPException(status_code=400, detail='Email already exists')
            
            # Create user in Supabase
            is_admin = payload.email == "admin@example.com"
            result = await supabase_client.create_user(payload.email, payload.password, is_admin)
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return {"message": "User created successfully", "email": payload.email}
        except HTTPException:
            raise
        except Exception as e:
            print(f"Supabase signup error: {e}")
            # Fall through to JSON fallback
    
    # Fallback to JSON file
    users = await load_users()
    
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
        "password": payload.password[:72],  # Store plain text for demo
        "created_at": datetime.now().isoformat(),
        "is_admin": payload.email == "admin@example.com"  # Admin email gets admin rights
    }
    
    await save_users(users)
    return {"message": "User created successfully", "email": payload.email}

@app.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token"""
    print(f"Login attempt for: {form_data.username}")  # Debug log
    
    # Try Supabase first
    if supabase_client.is_enabled():
        try:
            user = await supabase_client.get_user(form_data.username)
            if user and user['password'] == form_data.password:
                token = create_access_token({"sub": form_data.username, "is_admin": user.get("is_admin", False)})
                return {
                    "access_token": token, 
                    "token_type": "bearer",
                    "email": form_data.username,
                    "is_admin": user.get("is_admin", False)
                }
            elif user:
                print(f"Password mismatch for user: {form_data.username}")
                raise HTTPException(status_code=401, detail='Invalid email or password')
            else:
                print(f"User not found in Supabase: {form_data.username}")
                # Fall through to JSON fallback
        except HTTPException:
            raise
        except Exception as e:
            print(f"Supabase login error: {e}")
            # Fall through to JSON fallback
    
    # Fallback to JSON file
    users = await load_users()
    
    if not users:
        # Create default users if none exist
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
    
    # Try to find user by email (form_data.username will contain email)
    user = users.get(form_data.username)
    if not user:
        print(f"User not found: {form_data.username}")  # Debug log
        print(f"Available users: {list(users.keys())}")  # Debug log
        raise HTTPException(status_code=401, detail='Invalid email or password')
    
    print(f"User found: {form_data.username}")  # Debug log
    print(f"Stored password: {user['password']}")  # Debug log
    print(f"Provided password: {form_data.password}")  # Debug log
    
    # Simple password comparison for demo
    password_valid = (form_data.password == user['password'])
    
    print(f"Password valid: {password_valid}")  # Debug log
    
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
async def predict(payload: PredictIn, current_user: str = Depends(get_current_user_from_token)):
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
        'premium_annual_inr': payload.premium_annual_inr if payload.premium_annual_inr is not None else 0.0
    }
    
    X = pd.DataFrame([input_data])
    
    try:
        # Make prediction
        prediction = model.predict(X)[0]
        
        # Calculate confidence (using prediction variance across trees)
        confidence = 0.0
        try:
            if hasattr(model.named_steps['regressor'], 'estimators_'):
                # Get predictions from individual trees
                preprocessed_X = model.named_steps['preprocessor'].transform(X)
                tree_predictions = [tree.predict(preprocessed_X)[0] for tree in model.named_steps['regressor'].estimators_]
                confidence = float(1.0 / (1.0 + np.std(tree_predictions)))  # Higher std = lower confidence
        except Exception:
            confidence = 0.5  # Default confidence
        
        final_prediction = float(max(0, prediction))
        
        # Store prediction in Supabase
        if supabase_client.is_enabled():
            try:
                await supabase_client.store_prediction(
                    user_email=current_user,
                    input_data=input_data,
                    prediction=final_prediction,
                    confidence=confidence
                )
            except Exception as e:
                print(f"Error storing prediction in Supabase: {e}")
        
        return PredictResponse(
            prediction=final_prediction,
            confidence=confidence,
            input_data=input_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get('/stats', response_model=StatsResponse)
async def get_stats():
    """Get dataset statistics"""
    df = None
    
    # Try to get data from Supabase first
    if supabase_client.is_enabled():
        try:
            df = await supabase_client.get_latest_dataset()
            if df is not None:
                print("Using dataset from Supabase")
        except Exception as e:
            print(f"Error getting dataset from Supabase: {e}")
    
    # Fallback to local CSV files
    if df is None:
        dataset_to_use = None
        
        # First try the current CSV_PATH
        if os.path.exists(CSV_PATH):
            dataset_to_use = CSV_PATH
        else:
            # Look for any CSV file in the data directory
            data_dir = "data"
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith('.csv'):
                        dataset_to_use = os.path.join(data_dir, file)
                        break
        
        if not dataset_to_use:
            raise HTTPException(status_code=404, detail='No dataset found. Please upload a dataset first.')
        
        df = pd.read_csv(dataset_to_use)
        print("Using local CSV dataset")
    
    try:
        
        # Basic statistics
        stats = StatsResponse(
            total_policies=int(len(df)),
            avg_premium=float(df['premium_annual_inr'].mean()),
            avg_claim=float(df['claim_amount_inr'].mean()),
            avg_age=float(df['age'].mean()),
            avg_bmi=float(df['bmi'].mean()),
            smoker_percentage=float((df['smoker'] == 'Yes').mean() * 100),
            regions=df['region'].value_counts().to_dict(),
            gender_distribution=df['gender'].value_counts().to_dict()
        )
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")

@app.get('/claims-analysis', response_model=ClaimsAnalysis)
def get_claims_analysis():
    """Get detailed claims analysis"""
    # Find an available dataset file
    dataset_to_use = None
    
    # First try the current CSV_PATH
    if os.path.exists(CSV_PATH):
        dataset_to_use = CSV_PATH
    else:
        # Look for any CSV file in the data directory
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
            'claim_amount_inr': 'mean',
            'premium_annual_inr': 'mean'
        }).to_dict()
        
        # Premium vs Claims correlation
        premium_bins = pd.qcut(df['premium_annual_inr'], q=5, labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])
        premium_vs_claims = df.groupby(premium_bins)['claim_amount_inr'].mean().to_dict()
        
        return ClaimsAnalysis(
            age_groups=age_groups,
            region_analysis=region_analysis,
            smoker_analysis=smoker_analysis,
            premium_vs_claims=premium_vs_claims
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
    
    # Get feature importance
    try:
        feature_importance = get_feature_importance(model)
        info["feature_importance"] = feature_importance
    except Exception as e:
        info["feature_importance_error"] = str(e)
    
    return info

@app.post('/admin/upload')
async def admin_upload(file: UploadFile = File(...), current_user: str = Depends(get_current_user_from_token)):
    """Upload new dataset and retrain model (Admin only)"""
    # Check if user is admin
    if supabase_client.is_enabled():
        try:
            user = await supabase_client.get_user(current_user)
            if not user or not user.get("is_admin", False):
                raise HTTPException(status_code=403, detail="Admin access required")
        except Exception as e:
            print(f"Error checking admin status in Supabase: {e}")
            # Fall back to JSON check
            users = await load_users()
            user = users.get(current_user, {})
            if not user.get("is_admin", False):
                raise HTTPException(status_code=403, detail="Admin access required")
    else:
        users = await load_users()
        user = users.get(current_user, {})
        if not user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Clean filename to avoid path issues
        import re
        clean_filename = re.sub(r'[^\w\-_\.]', '_', file.filename)
        if not clean_filename.endswith('.csv'):
            clean_filename += '.csv'
        
        # Save uploaded file
        file_path = os.path.join(data_dir, clean_filename)
        
        # Read file content
        content = file.file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Write file to disk
        with open(file_path, 'wb') as f:
            f.write(content)
        
        print(f"File saved to: {file_path}")  # Debug log
        
        # Validate CSV
        try:
            df = pd.read_csv(file_path)
            required_columns = ['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr', 'claim_amount_inr']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                os.remove(file_path)  # Remove invalid file
                raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}")
            
            # Store dataset in Supabase
            if supabase_client.is_enabled():
                try:
                    metadata = {
                        "uploaded_by": current_user,
                        "original_filename": file.filename,
                        "file_size": len(content)
                    }
                    result = await supabase_client.store_dataset(clean_filename, df, metadata)
                    if "error" in result:
                        print(f"Error storing dataset in Supabase: {result['error']}")
                    else:
                        print(f"Dataset stored in Supabase with ID: {result.get('dataset_id')}")
                except Exception as e:
                    print(f"Error storing dataset in Supabase: {e}")
        
        except pd.errors.EmptyDataError:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        except Exception as e:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")
        
        # Retrain model with the uploaded dataset
        print(f"Starting model training with dataset: {file_path}")
        from train import train
        try:
            # Verify file exists before training
            if not os.path.exists(file_path):
                raise HTTPException(status_code=500, detail=f"File not found after upload: {file_path}")
            
            new_model = train(dataset_path=file_path)
            if new_model:
                global model, CSV_PATH
                model = new_model
                CSV_PATH = file_path
                print(f"Model training successful. New CSV_PATH: {CSV_PATH}")
                return {"message": f"File uploaded successfully and model retrained. Dataset has {len(df)} rows."}
            else:
                return {"message": "File uploaded but model training failed - no model returned"}
        except Exception as e:
            print(f"Training error: {str(e)}")  # Debug log
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
        
        from train import train
        global model, CSV_PATH
        
        # Use the most recent CSV file or the current CSV_PATH if it exists
        dataset_to_use = CSV_PATH if os.path.exists(CSV_PATH) else available_files[0]
        new_model = train(dataset_path=dataset_to_use)
        if new_model:
            model = new_model
            # Update CSV_PATH to the file we actually used
            CSV_PATH = dataset_to_use
            return {"message": f"Model retrained successfully using {os.path.basename(dataset_to_use)}"}
        else:
            raise HTTPException(status_code=500, detail="Model training failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
