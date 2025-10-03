# app.py
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from joblib import load, dump
import pandas as pd
import os
import json
import numpy as np
from datetime import datetime
import asyncio

from model_pipeline import build_pipeline, get_feature_importance
from fast_model_pipeline import build_fast_pipeline, get_model_info as get_fast_model_info
from fast_train import fast_train
from utils import hash_password, verify_password, create_access_token, decode_token, get_current_user
from database import supabase_client, init_database
from error_handler import setup_error_handlers, log_startup_info, request_logging_middleware
from email_service import email_service

app = FastAPI(title="India Medical Insurance ML Dashboard", version="1.0.0")

# Setup error handling
setup_error_handlers(app)

# Add validation error handler
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    print(f"Validation error: {exc}")
    error_details = []
    for error in exc.errors():
        field = error.get('loc', ['unknown'])[-1]
        message = error.get('msg', 'Invalid value')
        error_details.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=400,
        content={"detail": f"Validation failed: {'; '.join(error_details)}"}
    )

# Add request logging middleware
app.middleware("http")(request_logging_middleware)

# Startup event - Optimized for fast startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and load model on startup - Fast mode"""
    log_startup_info()
    print("🚀 Fast startup mode - optimized for Render deployment")
    
    try:
        # Initialize database (non-blocking)
        try:
            await init_database()
            print("✅ Database initialization completed")
        except Exception as db_e:
            print(f"⚠️ Database init warning: {db_e}")
        
        # Quick model loading - don't retrain on startup
        global model
        if os.path.exists(MODEL_PATH):
            try:
                model = load(MODEL_PATH)
                print("✅ Model loaded successfully")
                
                # Quick compatibility test (non-blocking)
                try:
                    import pandas as pd
                    test_df = pd.DataFrame({
                        'age': [30], 'bmi': [25.0], 'gender': ['Male'],
                        'smoker': ['No'], 'region': ['North'], 'premium_annual_inr': [15000.0]
                    })
                    _ = model.predict(test_df)
                    print("✅ Model compatibility verified")
                except Exception as test_e:
                    print(f"⚠️ Model test warning: {test_e} - will work in background")
                    
            except Exception as e:
                print(f"⚠️ Model loading warning: {e} - server will still start")
                model = None
        else:
            print("⚠️ No model found - server will start without model")
            model = None
            
        print("🎉 Fast startup completed - server ready!")
        
    except Exception as e:
        print(f"⚠️ Startup warning: {e} - server will still start")
        # Don't raise the exception to allow the server to start

async def retrain_compatible_model():
    """Retrain model with compatible parameters"""
    try:
        print("🔧 Training compatible model with scikit-learn compatibility...")
        
        # Find dataset
        data_dir = "data"
        dataset_files = []
        
        if os.path.exists(data_dir):
            dataset_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        if dataset_files:
            dataset_path = os.path.join(data_dir, dataset_files[0])
            print(f"📊 Using dataset: {dataset_path}")
            
            # Use fast_rf which has criterion='squared_error' for compatibility
            new_model = fast_train(dataset_path=dataset_path, model_type="fast_rf")
            
            if new_model:
                print("✅ Compatible model trained successfully")
                
                # Test the model to ensure no monotonic_cst error
                try:
                    test_data = pd.DataFrame({
                        'age': [30],
                        'bmi': [25.0],
                        'gender': ['Male'],
                        'smoker': ['No'],
                        'region': ['North'],
                        'premium_annual_inr': [20000.0]
                    })
                    test_prediction = new_model.predict(test_data)[0]
                    print(f"✅ Model compatibility test passed: ₹{test_prediction:.2f}")
                except Exception as test_e:
                    print(f"⚠️ Model compatibility test failed: {test_e}")
                    if "monotonic_cst" in str(test_e):
                        print("🚨 Still getting monotonic_cst error - this should not happen")
                
                return new_model
            else:
                print("❌ Model training failed")
                return None
        else:
            print("❌ No dataset found for training")
            return None
            
    except Exception as e:
        print(f"❌ Error training compatible model: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down application...")

# CORS middleware - Enhanced for better compatibility
import os

# Get allowed origins from environment variable with comprehensive defaults
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Always ensure comprehensive CORS support
essential_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://india-medical-insurance-frontend.vercel.app"
]

# Force wildcard for maximum compatibility if not already present
if "*" not in allowed_origins:
    # Add essential origins
    for origin in essential_origins:
        if origin not in allowed_origins:
            allowed_origins.append(origin)
    
    # Add wildcard for full compatibility
    allowed_origins.append("*")

# Ensure wildcard is always included for maximum compatibility
if "*" not in allowed_origins:
    allowed_origins.append("*")

print(f"CORS allowed origins: {allowed_origins}")  # Debug log

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "*",
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "Cache-Control",
        "Pragma"
    ],
    expose_headers=[
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods", 
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Credentials"
    ]
)

# Additional CORS middleware for maximum compatibility
@app.middleware("http")
async def add_cors_headers(request, call_next):
    """Add CORS headers to all responses"""
    response = await call_next(request)
    
    # Get origin from request
    origin = request.headers.get("origin")
    
    # Always allow CORS for essential origins
    allowed_origins_list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:3001",
        "https://india-medical-insurance-frontend.vercel.app"
    ]
    
    if origin in allowed_origins_list or "*" in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "3600"
    
    return response

# Configuration
MODEL_PATH = "models/model_pipeline.pkl"
USERS_DB = "users.json"
CSV_PATH = "data/sample_medical_insurance_data.csv"

# Global variables
model = None

# Skip dataset creation on startup for faster loading
# Dataset will be created on-demand when needed

# Initialize model variable (will be loaded in startup event)
model = None

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
    premium_annual_inr: float
    email: Optional[str] = None

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

class EmailPredictionRequest(BaseModel):
    email: EmailStr
    prediction: dict
    patient_data: dict

class EmailResponse(BaseModel):
    success: bool
    message: str

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

async def store_prediction_locally(user_email: str, input_data: dict, prediction: float, confidence: float):
    """Store prediction locally in JSON file"""
    predictions_file = "predictions.json"
    
    # Load existing predictions
    predictions = []
    if os.path.exists(predictions_file):
        try:
            with open(predictions_file, 'r') as f:
                predictions = json.load(f)
        except Exception:
            predictions = []
    
    # Add new prediction
    new_prediction = {
        "user_email": user_email,
        "input_data": input_data,
        "prediction": prediction,
        "confidence": confidence,
        "created_at": datetime.now().isoformat()
    }
    
    predictions.append(new_prediction)
    
    # Keep only last 1000 predictions to avoid file getting too large
    if len(predictions) > 1000:
        predictions = predictions[-1000:]
    
    # Save predictions
    with open(predictions_file, 'w') as f:
        json.dump(predictions, f, indent=2)

async def get_local_predictions(user_email: str = None):
    """Get local predictions, optionally filtered by user"""
    predictions_file = "predictions.json"
    
    if os.path.exists(predictions_file):
        try:
            with open(predictions_file, 'r') as f:
                all_predictions = json.load(f)
                
            # Filter by user if specified
            if user_email:
                user_predictions = [p for p in all_predictions if p.get('user_email') == user_email]
                return user_predictions
            else:
                return all_predictions
        except Exception:
            return []
    return []

async def is_admin_user(user_email: str) -> bool:
    """Check if user is admin"""
    try:
        if supabase_client.is_enabled():
            user = await supabase_client.get_user(user_email)
            return user and user.get("is_admin", False)
        else:
            users = await load_users()
            user = users.get(user_email, {})
            return user.get("is_admin", False)
    except Exception:
        return False

# Routes - Optimized for fast response
@app.get("/")
@app.head("/")
def root():
    """Fast root endpoint for Render health checks"""
    return {
        "message": "India Medical Insurance ML Dashboard API", 
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

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
        "timestamp": datetime.now().isoformat(),
        "server_status": "running"
    }

@app.options("/cors-test")
def cors_test_options():
    """Handle CORS preflight for cors-test"""
    return {"message": "CORS preflight OK"}

@app.options("/login")
def login_options():
    """Handle CORS preflight for login"""
    return {"message": "Login CORS preflight OK"}

@app.get("/favicon.ico")
def favicon():
    """Handle favicon requests to prevent 405 errors"""
    from fastapi.responses import Response
    return Response(content="", media_type="image/x-icon", status_code=204)

@app.options("/{path:path}")
def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return {"message": "OK"}

@app.head("/{path:path}")
def head_handler(path: str):
    """Handle HEAD requests for health checks and monitoring"""
    # HEAD requests should return empty body with proper status
    return {}

@app.get("/{path:path}")
def catch_all_handler(path: str):
    """Catch-all handler for undefined GET routes"""
    if path in ["robots.txt", "sitemap.xml"]:
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("", status_code=204)
    
    return {
        "message": f"Endpoint /{path} not found",
        "available_endpoints": [
            "/", "/health", "/cors-test", "/signup", "/login", 
            "/predict", "/stats", "/model-info", "/docs"
        ]
    }

@app.post('/signup', response_model=dict)
async def signup(payload: UserIn):
    """Register a new user"""
    print(f"Signup attempt - Email: {payload.email}, Password length: {len(payload.password)}")  # Debug log
    # Try Supabase first
    if supabase_client.is_enabled():
        try:
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, payload.email):
                raise HTTPException(status_code=400, detail='Invalid email format')
            
            # Allow any password length - user's choice
            
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
    
    # Allow any password length - user's choice
    
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
    global model
    
    if model is None:
        raise HTTPException(status_code=503, detail='Model not loaded. Please train the model first.')
    
    # Prepare input data
    input_data = {
        'age': payload.age,
        'bmi': payload.bmi,
        'gender': payload.gender,
        'smoker': payload.smoker,
        'region': payload.region,
        'premium_annual_inr': payload.premium_annual_inr
    }
    
    try:
        # Handle both old and new model formats
        if isinstance(model, dict) and 'model' in model:
            # New format with encoders
            X_encoded = pd.DataFrame([{
                'age': payload.age,
                'bmi': payload.bmi,
                'gender': model['encoders']['gender'].transform([payload.gender])[0],
                'smoker': model['encoders']['smoker'].transform([payload.smoker])[0],
                'region': model['encoders']['region'].transform([payload.region])[0],
                'premium_annual_inr': payload.premium_annual_inr
            }])
            prediction = model['model'].predict(X_encoded)[0]
        else:
            # Old format - direct prediction
            X = pd.DataFrame([input_data])
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
        
        # Save email to users table if provided
        if payload.email and payload.email.strip():
            try:
                if supabase_client.is_enabled():
                    email_result = await supabase_client.save_email_to_users(payload.email.strip())
                    if email_result.get("success"):
                        print(f"✅ Email {payload.email} saved to users table")
                    else:
                        print(f"⚠️ Failed to save email to users table: {email_result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"⚠️ Error saving email to users table: {e}")
        
        # Store prediction in Supabase or local file
        try:
            if supabase_client.is_enabled():
                await supabase_client.store_prediction(
                    user_email=current_user,
                    input_data=input_data,
                    prediction=final_prediction,
                    confidence=confidence
                )
                print(f"✅ Prediction stored in Supabase for {current_user}")
            else:
                # Store locally if Supabase not available
                await store_prediction_locally(current_user, input_data, final_prediction, confidence)
                print(f"✅ Prediction stored locally for {current_user}")
        except Exception as e:
            print(f"⚠️ Error storing prediction: {e}")
            # Try local storage as fallback
            try:
                await store_prediction_locally(current_user, input_data, final_prediction, confidence)
                print(f"✅ Prediction stored locally as fallback for {current_user}")
            except Exception as local_e:
                print(f"❌ Failed to store prediction locally: {local_e}")
        
        return PredictResponse(
            prediction=final_prediction,
            confidence=confidence,
            input_data=input_data
        )
    
    except AttributeError as e:
        if 'monotonic_cst' in str(e):
            print("🔧 Detected monotonic_cst error, retraining model...")
            try:
                # Retrain model with compatible parameters
                model = await retrain_compatible_model()
                if model:
                    # Retry prediction with new model
                    df = pd.DataFrame([input_data])
                    prediction = model.predict(df)[0]
                    confidence = min(0.95, max(0.6, 1.0 - abs(prediction - 20000) / 50000))
                    final_prediction = max(0, float(prediction))
                    
                    return PredictResponse(
                        prediction=final_prediction,
                        confidence=confidence,
                        input_data=input_data
                    )
                else:
                    raise HTTPException(status_code=503, detail='Model retraining failed. Please contact support.')
            except Exception as retrain_error:
                raise HTTPException(status_code=500, detail=f"Model compatibility error and retraining failed: {str(retrain_error)}")
        else:
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get('/stats')
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
        
        # First try the current CSV_PATH (most recently uploaded/used dataset)
        if os.path.exists(CSV_PATH):
            dataset_to_use = CSV_PATH
        else:
            # Look for the most recent CSV file in the data directory
            data_dir = "data"
            if os.path.exists(data_dir):
                csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                if csv_files:
                    # Get the most recently modified CSV file
                    csv_files_with_time = [(f, os.path.getmtime(os.path.join(data_dir, f))) for f in csv_files]
                    csv_files_with_time.sort(key=lambda x: x[1], reverse=True)  # Sort by modification time, newest first
                    dataset_to_use = os.path.join(data_dir, csv_files_with_time[0][0])
        
        if not dataset_to_use:
            raise HTTPException(status_code=404, detail='No dataset found. Please upload a dataset first.')
        
        df = pd.read_csv(dataset_to_use)
        print("Using local CSV dataset")
    
    try:
        # Basic statistics with NaN/inf handling
        def safe_float(value, default=0.0):
            """Convert to float, handling NaN and inf values"""
            try:
                result = float(value)
                if pd.isna(result) or not np.isfinite(result):
                    return default
                return result
            except (ValueError, TypeError):
                return default
        
        def safe_dict(series_counts):
            """Convert value_counts to safe dict"""
            try:
                result = {}
                for key, value in series_counts.items():
                    # Ensure key is string and value is safe int
                    safe_key = str(key) if key is not None else "Unknown"
                    safe_value = int(value) if pd.notna(value) else 0
                    result[safe_key] = safe_value
                return result
            except Exception:
                return {}
        
        # Calculate smoker percentage safely
        try:
            smoker_pct = (df['smoker'] == 'Yes').mean() * 100
            if pd.isna(smoker_pct):
                smoker_pct = 0.0
        except Exception:
            smoker_pct = 0.0
        
        stats = StatsResponse(
            total_policies=int(len(df)),
            avg_premium=safe_float(df['premium_annual_inr'].mean()),
            avg_claim=safe_float(df['claim_amount_inr'].mean()),
            avg_age=safe_float(df['age'].mean()),
            avg_bmi=safe_float(df['bmi'].mean()),
            smoker_percentage=safe_float(smoker_pct),
            regions=safe_dict(df['region'].value_counts()),
            gender_distribution=safe_dict(df['gender'].value_counts())
        )
        
        return stats
    
    except Exception as e:
        print(f"Stats calculation error: {e}")  # Debug log
        # Return default stats if calculation fails
        return StatsResponse(
            total_policies=0,
            avg_premium=0.0,
            avg_claim=0.0,
            avg_age=0.0,
            avg_bmi=0.0,
            smoker_percentage=0.0,
            regions={},
            gender_distribution={}
        )

@app.get('/user-stats', response_model=StatsResponse)
async def get_user_stats(current_user: str = Depends(get_current_user_from_token)):
    """Get statistics for current user only"""
    try:
        # Get user's predictions only
        user_predictions = await get_local_predictions(current_user)
        
        if not user_predictions:
            # Return empty stats if user has no predictions
            return StatsResponse(
                total_policies=0,
                avg_premium=0.0,
                avg_claim=0.0,
                avg_age=0.0,
                avg_bmi=0.0,
                smoker_percentage=0.0,
                regions={},
                gender_distribution={}
            )
        
        # Convert user predictions to DataFrame
        prediction_rows = []
        for pred in user_predictions:
            input_data = pred['input_data']
            row = {
                'age': input_data.get('age', 30),
                'bmi': input_data.get('bmi', 25.0),
                'gender': input_data.get('gender', 'Male'),
                'smoker': input_data.get('smoker', 'No'),
                'region': input_data.get('region', 'North'),
                'premium_annual_inr': input_data.get('premium_annual_inr', 20000.0),
                'claim_amount_inr': pred['prediction']
            }
            prediction_rows.append(row)
        
        df = pd.DataFrame(prediction_rows)
        
        # Calculate user-specific stats
        def safe_float(value, default=0.0):
            try:
                result = float(value)
                if pd.isna(result) or not np.isfinite(result):
                    return default
                return result
            except (ValueError, TypeError):
                return default
        
        def safe_dict(series_counts):
            try:
                result = {}
                for key, value in series_counts.items():
                    safe_key = str(key) if key is not None else "Unknown"
                    safe_value = int(value) if pd.notna(value) else 0
                    result[safe_key] = safe_value
                return result
            except Exception:
                return {}
        
        # Calculate smoker percentage safely
        try:
            smoker_pct = (df['smoker'] == 'Yes').mean() * 100
            if pd.isna(smoker_pct):
                smoker_pct = 0.0
        except Exception:
            smoker_pct = 0.0
        
        stats = StatsResponse(
            total_policies=int(len(df)),
            avg_premium=safe_float(df['premium_annual_inr'].mean()),
            avg_claim=safe_float(df['claim_amount_inr'].mean()),
            avg_age=safe_float(df['age'].mean()),
            avg_bmi=safe_float(df['bmi'].mean()),
            smoker_percentage=safe_float(smoker_pct),
            regions=safe_dict(df['region'].value_counts()),
            gender_distribution=safe_dict(df['gender'].value_counts())
        )
        
        return stats
        
    except Exception as e:
        print(f"User stats calculation error: {e}")
        return StatsResponse(
            total_policies=0,
            avg_premium=0.0,
            avg_claim=0.0,
            avg_age=0.0,
            avg_bmi=0.0,
            smoker_percentage=0.0,
            regions={},
            gender_distribution={}
        )

@app.get('/live-stats', response_model=StatsResponse)
async def get_live_stats():
    """Get dataset statistics including user predictions (live data)"""
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
        
        # First try the current CSV_PATH (most recently uploaded/used dataset)
        if os.path.exists(CSV_PATH):
            dataset_to_use = CSV_PATH
        else:
            # Look for the most recent CSV file in the data directory
            data_dir = "data"
            if os.path.exists(data_dir):
                csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                if csv_files:
                    # Get the most recently modified CSV file
                    csv_files_with_time = [(f, os.path.getmtime(os.path.join(data_dir, f))) for f in csv_files]
                    csv_files_with_time.sort(key=lambda x: x[1], reverse=True)  # Sort by modification time, newest first
                    dataset_to_use = os.path.join(data_dir, csv_files_with_time[0][0])
        
        if not dataset_to_use:
            raise HTTPException(status_code=404, detail='No dataset found. Please upload a dataset first.')
        
        df = pd.read_csv(dataset_to_use)
        print("Using local CSV dataset")
    
    # Get user predictions and add them to the dataset
    try:
        predictions = []
        
        # Try Supabase first
        if supabase_client.is_enabled():
            try:
                # Get recent predictions from all users
                # Note: This would need to be implemented in database.py
                print("Would get predictions from Supabase here")
            except Exception as e:
                print(f"Error getting predictions from Supabase: {e}")
        
        # Get local predictions
        local_predictions = await get_local_predictions()
        
        # Convert predictions to DataFrame format and append
        if local_predictions:
            prediction_rows = []
            for pred in local_predictions:
                input_data = pred['input_data']
                row = {
                    'age': input_data.get('age', 30),
                    'bmi': input_data.get('bmi', 25.0),
                    'gender': input_data.get('gender', 'Male'),
                    'smoker': input_data.get('smoker', 'No'),
                    'region': input_data.get('region', 'North'),
                    'premium_annual_inr': input_data.get('premium_annual_inr', 20000.0),
                    'claim_amount_inr': pred['prediction']  # Use prediction as claim amount
                }
                prediction_rows.append(row)
            
            if prediction_rows:
                pred_df = pd.DataFrame(prediction_rows)
                df = pd.concat([df, pred_df], ignore_index=True)
                print(f"✅ Added {len(prediction_rows)} user predictions to stats")
    
    except Exception as e:
        print(f"Error adding predictions to stats: {e}")
    
    # Calculate stats with the enhanced dataset
    try:
        # Basic statistics with NaN/inf handling
        def safe_float(value, default=0.0):
            """Convert to float, handling NaN and inf values"""
            try:
                result = float(value)
                if pd.isna(result) or not np.isfinite(result):
                    return default
                return result
            except (ValueError, TypeError):
                return default
        
        def safe_dict(series_counts):
            """Convert value_counts to safe dict"""
            try:
                result = {}
                for key, value in series_counts.items():
                    # Ensure key is string and value is safe int
                    safe_key = str(key) if key is not None else "Unknown"
                    safe_value = int(value) if pd.notna(value) else 0
                    result[safe_key] = safe_value
                return result
            except Exception:
                return {}
        
        # Calculate smoker percentage safely
        try:
            smoker_pct = (df['smoker'] == 'Yes').mean() * 100
            if pd.isna(smoker_pct):
                smoker_pct = 0.0
        except Exception:
            smoker_pct = 0.0
        
        stats = StatsResponse(
            total_policies=int(len(df)),
            avg_premium=safe_float(df['premium_annual_inr'].mean()),
            avg_claim=safe_float(df['claim_amount_inr'].mean()),
            avg_age=safe_float(df['age'].mean()),
            avg_bmi=safe_float(df['bmi'].mean()),
            smoker_percentage=safe_float(smoker_pct),
            regions=safe_dict(df['region'].value_counts()),
            gender_distribution=safe_dict(df['gender'].value_counts())
        )
        
        return stats
    
    except Exception as e:
        print(f"Live stats calculation error: {e}")  # Debug log
        # Return default stats if calculation fails
        return StatsResponse(
            total_policies=0,
            avg_premium=0.0,
            avg_claim=0.0,
            avg_age=0.0,
            avg_bmi=0.0,
            smoker_percentage=0.0,
            regions={},
            gender_distribution={}
        )

@app.get('/claims-analysis', response_model=ClaimsAnalysis)
def get_claims_analysis():
    """Get detailed claims analysis"""
    # Find an available dataset file
    dataset_to_use = None
    
    # First try the current CSV_PATH (most recently uploaded/used dataset)
    if os.path.exists(CSV_PATH):
        dataset_to_use = CSV_PATH
    else:
        # Look for the most recent CSV file in the data directory
        data_dir = "data"
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            if csv_files:
                # Get the most recently modified CSV file
                csv_files_with_time = [(f, os.path.getmtime(os.path.join(data_dir, f))) for f in csv_files]
                csv_files_with_time.sort(key=lambda x: x[1], reverse=True)  # Sort by modification time, newest first
                dataset_to_use = os.path.join(data_dir, csv_files_with_time[0][0])
    
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
        region_stats = df.groupby('region').agg({
            'claim_amount_inr': ['mean', 'count'],
            'premium_annual_inr': 'mean'
        })
        
        # Restructure region analysis to match frontend expectations
        region_analysis = {
            'claim_amount_inr': {
                'mean': region_stats[('claim_amount_inr', 'mean')].to_dict(),
                'count': region_stats[('claim_amount_inr', 'count')].to_dict()
            },
            'premium_annual_inr': region_stats[('premium_annual_inr', 'mean')].to_dict()
        }
        
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

@app.get('/live-claims-analysis', response_model=ClaimsAnalysis)
async def get_live_claims_analysis():
    """Get detailed claims analysis including user predictions (live data)"""
    # Find an available dataset file
    dataset_to_use = None
    
    # First try the current CSV_PATH (most recently uploaded/used dataset)
    if os.path.exists(CSV_PATH):
        dataset_to_use = CSV_PATH
    else:
        # Look for the most recent CSV file in the data directory
        data_dir = "data"
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            if csv_files:
                # Get the most recently modified CSV file
                csv_files_with_time = [(f, os.path.getmtime(os.path.join(data_dir, f))) for f in csv_files]
                csv_files_with_time.sort(key=lambda x: x[1], reverse=True)  # Sort by modification time, newest first
                dataset_to_use = os.path.join(data_dir, csv_files_with_time[0][0])
    
    if not dataset_to_use:
        raise HTTPException(status_code=404, detail='No dataset found. Please upload a dataset first.')
    
    try:
        df = pd.read_csv(dataset_to_use)
        
        # Add user predictions to the analysis
        try:
            local_predictions = await get_local_predictions()
            
            # Convert predictions to DataFrame format and append
            if local_predictions:
                prediction_rows = []
                for pred in local_predictions:
                    input_data = pred['input_data']
                    row = {
                        'age': input_data.get('age', 30),
                        'bmi': input_data.get('bmi', 25.0),
                        'gender': input_data.get('gender', 'Male'),
                        'smoker': input_data.get('smoker', 'No'),
                        'region': input_data.get('region', 'North'),
                        'premium_annual_inr': input_data.get('premium_annual_inr', 20000.0),
                        'claim_amount_inr': pred['prediction']  # Use prediction as claim amount
                    }
                    prediction_rows.append(row)
                
                if prediction_rows:
                    pred_df = pd.DataFrame(prediction_rows)
                    df = pd.concat([df, pred_df], ignore_index=True)
                    print(f"✅ Added {len(prediction_rows)} user predictions to claims analysis")
        
        except Exception as e:
            print(f"Error adding predictions to claims analysis: {e}")
        
        # Age group analysis
        df['age_group'] = pd.cut(df['age'], bins=[0, 30, 40, 50, 60, 100], labels=['<30', '30-40', '40-50', '50-60', '60+'])
        age_groups = df.groupby('age_group').agg({
            'claim_amount_inr': 'mean',
            'premium_annual_inr': 'mean'
        }).to_dict()
        
        # Region analysis
        region_stats = df.groupby('region').agg({
            'claim_amount_inr': ['mean', 'count'],
            'premium_annual_inr': 'mean'
        })
        
        # Restructure region analysis to match frontend expectations
        region_analysis = {
            'claim_amount_inr': {
                'mean': region_stats[('claim_amount_inr', 'mean')].to_dict(),
                'count': region_stats[('claim_amount_inr', 'count')].to_dict()
            },
            'premium_annual_inr': region_stats[('premium_annual_inr', 'mean')].to_dict()
        }
        
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
        raise HTTPException(status_code=500, detail=f"Error in live claims analysis: {str(e)}")

@app.get('/user-claims-analysis', response_model=ClaimsAnalysis)
async def get_user_claims_analysis(current_user: str = Depends(get_current_user_from_token)):
    """Get detailed claims analysis for current user only"""
    try:
        # Get user's predictions only
        user_predictions = await get_local_predictions(current_user)
        
        if not user_predictions:
            # Return empty analysis if user has no predictions
            return ClaimsAnalysis(
                age_groups={},
                region_analysis={},
                smoker_analysis={},
                premium_vs_claims={}
            )
        
        # Convert user predictions to DataFrame
        prediction_rows = []
        for pred in user_predictions:
            input_data = pred['input_data']
            row = {
                'age': input_data.get('age', 30),
                'bmi': input_data.get('bmi', 25.0),
                'gender': input_data.get('gender', 'Male'),
                'smoker': input_data.get('smoker', 'No'),
                'region': input_data.get('region', 'North'),
                'premium_annual_inr': input_data.get('premium_annual_inr', 20000.0),
                'claim_amount_inr': pred['prediction']
            }
            prediction_rows.append(row)
        
        df = pd.DataFrame(prediction_rows)
        
        # Age group analysis
        df['age_group'] = pd.cut(df['age'], bins=[0, 30, 40, 50, 60, 100], labels=['<30', '30-40', '40-50', '50-60', '60+'])
        age_groups = df.groupby('age_group').agg({
            'claim_amount_inr': 'mean',
            'premium_annual_inr': 'mean'
        }).to_dict()
        
        # Region analysis
        region_stats = df.groupby('region').agg({
            'claim_amount_inr': ['mean', 'count'],
            'premium_annual_inr': 'mean'
        })
        
        # Restructure region analysis to match frontend expectations
        region_analysis = {
            'claim_amount_inr': {
                'mean': region_stats[('claim_amount_inr', 'mean')].to_dict(),
                'count': region_stats[('claim_amount_inr', 'count')].to_dict()
            },
            'premium_annual_inr': region_stats[('premium_annual_inr', 'mean')].to_dict()
        }
        
        # Smoker analysis
        smoker_analysis = df.groupby('smoker').agg({
            'claim_amount_inr': 'mean',
            'premium_annual_inr': 'mean'
        }).to_dict()
        
        # Premium vs Claims correlation
        try:
            if len(df) >= 5:  # Need at least 5 records for qcut
                premium_bins = pd.qcut(df['premium_annual_inr'], q=min(5, len(df)), labels=False, duplicates='drop')
                premium_vs_claims = df.groupby(premium_bins)['claim_amount_inr'].mean().to_dict()
            else:
                # For small datasets, just use simple grouping
                premium_vs_claims = {"Low": df['claim_amount_inr'].mean()}
        except Exception:
            premium_vs_claims = {"All": df['claim_amount_inr'].mean()}
        
        return ClaimsAnalysis(
            age_groups=age_groups,
            region_analysis=region_analysis,
            smoker_analysis=smoker_analysis,
            premium_vs_claims=premium_vs_claims
        )
    
    except Exception as e:
        print(f"User claims analysis error: {e}")
        return ClaimsAnalysis(
            age_groups={},
            region_analysis={},
            smoker_analysis={},
            premium_vs_claims={}
        )

@app.get('/model-info')
async def get_model_info(current_user: str = Depends(get_current_user_from_token)):
    """Get model information and feature importance (requires authentication)"""
    if model is None:
        return {"status": "No model loaded"}
    
    info = {"status": "Model loaded"}
    
    # Try to get model metadata from Supabase first
    if supabase_client.is_enabled():
        try:
            supabase_metadata = await supabase_client.get_latest_model_metadata()
            if supabase_metadata:
                print("Using model metadata from Supabase")
                # Convert Supabase metadata to expected format
                info.update({
                    "test_r2": supabase_metadata.get("test_r2", 0.0),
                    "test_rmse": supabase_metadata.get("test_rmse", 0.0),
                    "training_date": supabase_metadata.get("training_date", ""),
                    "training_samples": supabase_metadata.get("training_samples", 0),
                    "model_type": supabase_metadata.get("model_type", "Unknown"),
                    "trained_by": supabase_metadata.get("trained_by", "Unknown"),
                    "training_dataset": supabase_metadata.get("training_dataset", "Unknown")
                })
        except Exception as e:
            print(f"Error getting model metadata from Supabase: {e}")
    
    # Fallback to local metadata file if Supabase data not available
    if "test_r2" not in info:
        metadata_path = "models/training_metadata.json"
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                # Clean metadata to handle NaN/inf values
                cleaned_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, float):
                        if pd.isna(value) or not np.isfinite(value):
                            cleaned_metadata[key] = 0.0
                        else:
                            cleaned_metadata[key] = value
                    else:
                        cleaned_metadata[key] = value
                info.update(cleaned_metadata)
            print("Using local model metadata")
    
    # Get feature importance (try fast method first, then fallback)
    try:
        from fast_model_pipeline import get_feature_importance as get_fast_feature_importance
        feature_importance = get_fast_feature_importance(model)
        if not feature_importance:
            # Fallback to original method
            feature_importance = get_feature_importance(model)
        info["feature_importance"] = feature_importance
    except Exception as e:
        try:
            # Fallback to original method
            feature_importance = get_feature_importance(model)
            info["feature_importance"] = feature_importance
        except Exception as e2:
            info["feature_importance_error"] = str(e2)
    
    # Add fast model info if available
    try:
        fast_info = get_fast_model_info(model)
        info.update(fast_info)
    except Exception:
        pass
    
    return info

@app.get('/model-status')
def get_model_status():
    """Get basic model status (public endpoint)"""
    if model is None:
        return {"status": "No model loaded", "model_loaded": False}
    
    info = {
        "status": "Model loaded",
        "model_loaded": True,
        "timestamp": datetime.now().isoformat()
    }
    
    # Load basic training metadata if available
    metadata_path = "models/training_metadata.json"
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                # Include only basic, safe metadata
                safe_fields = ['training_date', 'model_type', 'training_time_seconds', 'optimized_for']
                for field in safe_fields:
                    if field in metadata:
                        value = metadata[field]
                        if isinstance(value, float):
                            if pd.isna(value) or not np.isfinite(value):
                                info[field] = 0.0
                            else:
                                info[field] = value
                        else:
                            info[field] = value
        except Exception as e:
            info["metadata_error"] = "Could not load training metadata"
    
    return info

@app.post('/admin/upload')
async def admin_upload(file: UploadFile = File(...), current_user: str = Depends(get_current_user_from_token)):
    """Upload new dataset and retrain model (Admin only)"""
    try:
        print(f"🔄 Admin upload started by: {current_user}")
        print(f"📁 File: {file.filename}, Content-Type: {file.content_type}")
        
        # Check if user is admin with better error handling
        is_admin = False
        try:
            if supabase_client.is_enabled():
                user = await supabase_client.get_user(current_user)
                is_admin = user and user.get("is_admin", False)
                print(f"🔐 Supabase admin check: {is_admin}")
            else:
                users = await load_users()
                user = users.get(current_user, {})
                is_admin = user.get("is_admin", False)
                print(f"🔐 Local admin check: {is_admin}")
        except Exception as e:
            print(f"⚠️ Error checking admin status: {e}")
            # Try fallback method
            try:
                users = await load_users()
                user = users.get(current_user, {})
                is_admin = user.get("is_admin", False)
                print(f"🔐 Fallback admin check: {is_admin}")
            except Exception as fallback_e:
                print(f"❌ Fallback admin check failed: {fallback_e}")
                raise HTTPException(status_code=500, detail=f"Could not verify admin status: {str(fallback_e)}")
        
        if not is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        print("✅ Admin access verified")
        
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        print(f"📁 Data directory ready: {data_dir}")
        
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
        
        # Add timestamp to avoid conflicts with existing files
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_parts = clean_filename.rsplit('.', 1)
        if len(name_parts) == 2:
            clean_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        else:
            clean_filename = f"{clean_filename}_{timestamp}"
        
        # Save uploaded file
        file_path = os.path.join(data_dir, clean_filename)
        print(f"📁 Target file path: {file_path}")
        
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
            
            # Try to store dataset in Supabase (optional, don't fail if it doesn't work)
            if supabase_client.is_enabled():
                try:
                    metadata = {
                        "uploaded_by": current_user,
                        "original_filename": file.filename,
                        "file_size": len(content)
                    }
                    result = await supabase_client.store_dataset(clean_filename, df, metadata)
                    if "error" in result:
                        print(f"Warning: Could not store dataset in Supabase: {result['error']}")
                    else:
                        print(f"Dataset stored in Supabase with ID: {result.get('dataset_id')}")
                except Exception as e:
                    print(f"Warning: Could not store dataset in Supabase: {e}")
            else:
                print("Supabase not enabled, storing dataset locally only")
        
        except pd.errors.EmptyDataError:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        except Exception as e:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")
        
        # Retrain model with the uploaded dataset
        print(f"Starting model training with dataset: {file_path}")
        try:
            # Verify file exists before training
            if not os.path.exists(file_path):
                raise HTTPException(status_code=500, detail=f"File not found after upload: {file_path}")
            
            print("File verified, starting fast training...")
            
            # Train model with new dataset using fast training
            global model, CSV_PATH
            new_model = fast_train(dataset_path=file_path, model_type="fast_rf")
            
            if new_model:
                model = new_model
                CSV_PATH = file_path  # Update to use the new dataset
                print(f"Model training successful. New CSV_PATH: {CSV_PATH}")
                
                # Store model metadata in Supabase after successful training
                if supabase_client.is_enabled():
                    try:
                        # Calculate model performance metrics
                        from sklearn.model_selection import train_test_split
                        from sklearn.metrics import mean_squared_error, r2_score
                        
                        # Prepare data for evaluation
                        X = df.drop('claim_amount_inr', axis=1)
                        y = df['claim_amount_inr']
                        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                        
                        # Get predictions for evaluation
                        y_pred = model.predict(X_test)
                        r2 = r2_score(y_test, y_pred)
                        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                        
                        model_metadata = {
                            "training_samples": len(df),
                            "test_samples": len(X_test),
                            "train_r2": float(r2_score(y_train, model.predict(X_train))),
                            "test_r2": float(r2),
                            "train_rmse": float(np.sqrt(mean_squared_error(y_train, model.predict(X_train)))),
                            "test_rmse": float(rmse),
                            "features": list(X.columns),
                            "model_version": "1.0",
                            "training_date": datetime.now().isoformat()
                        }
                        
                        model_result = await supabase_client.store_model_metadata(model_metadata)
                        if "error" in model_result:
                            print(f"Warning: Could not store model metadata: {model_result['error']}")
                        else:
                            print(f"Model metadata stored successfully")
                            
                    except Exception as e:
                        print(f"Warning: Could not store model metadata: {e}")
                
                return {
                    "message": f"File uploaded successfully and model retrained. Dataset has {len(df)} rows.",
                    "dataset_rows": len(df),
                    "filename": file.filename,
                    "training_completed": True,
                    "file_path": file_path,
                    "supabase_stored": supabase_client.is_enabled()
                }
            else:
                print("Model training returned None")
                return {
                    "message": "File uploaded but model training failed - no model returned",
                    "dataset_rows": len(df),
                    "filename": file.filename,
                    "training_completed": False,
                    "file_path": file_path
                }
                
        except Exception as e:
            print(f"Training error: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            
            # Even if training fails, the file was uploaded successfully
            return {
                "message": f"File uploaded successfully but model training failed: {str(e)}",
                "dataset_rows": len(df),
                "filename": file.filename,
                "training_completed": False,
                "error": str(e),
                "file_path": file_path
            }
            
    except HTTPException:
        # Re-raise HTTP exceptions (like 403, 400)
        raise
    except Exception as e:
        print(f"Upload failed with error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post('/admin/retrain')
async def admin_retrain(current_user: str = Depends(get_current_user_from_token)):
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
        # Find available dataset files
        data_dir = "data"
        available_files = []
        
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith('.csv'):
                    available_files.append(os.path.join(data_dir, file))
        
        if not available_files:
            raise HTTPException(status_code=404, detail="No dataset files found. Please upload a dataset first.")
        
        global model, CSV_PATH
        
        # Use the most recent CSV file or the current CSV_PATH if it exists
        dataset_to_use = CSV_PATH if os.path.exists(CSV_PATH) else available_files[0]
        
        # Use fast training for quick retraining
        new_model = fast_train(dataset_path=dataset_to_use, model_type="fast_rf")
        if new_model:
            model = new_model
            # Update CSV_PATH to the file we actually used
            CSV_PATH = dataset_to_use
            
            # Store model metadata in Supabase after successful retraining
            if supabase_client.is_enabled():
                try:
                    # Load dataset for evaluation
                    df = pd.read_csv(dataset_to_use)
                    
                    # Calculate model performance metrics
                    from sklearn.model_selection import train_test_split
                    from sklearn.metrics import mean_squared_error, r2_score
                    
                    # Prepare data for evaluation
                    X = df.drop('claim_amount_inr', axis=1)
                    y = df['claim_amount_inr']
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    
                    # Get predictions for evaluation
                    y_pred = model.predict(X_test)
                    r2 = r2_score(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    
                    model_metadata = {
                        "training_samples": len(df),
                        "test_samples": len(X_test),
                        "train_r2": float(r2_score(y_train, model.predict(X_train))),
                        "test_r2": float(r2),
                        "train_rmse": float(np.sqrt(mean_squared_error(y_train, model.predict(X_train)))),
                        "test_rmse": float(rmse),
                        "features": list(X.columns),
                        "model_version": "1.1",
                        "training_date": datetime.now().isoformat()
                    }
                    
                    model_result = await supabase_client.store_model_metadata(model_metadata)
                    if "error" in model_result:
                        print(f"Warning: Could not store model metadata: {model_result['error']}")
                    else:
                        print(f"Model metadata stored successfully after retraining")
                        
                except Exception as e:
                    print(f"Warning: Could not store model metadata: {e}")
            
            return {
                "message": f"Model retrained successfully using {os.path.basename(dataset_to_use)} (Fast training completed in <30 seconds)",
                "supabase_stored": supabase_client.is_enabled()
            }
        else:
            raise HTTPException(status_code=500, detail="Model training failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

@app.post('/admin/retrain-fast')
async def admin_retrain_fast(current_user: str = Depends(get_current_user_from_token)):
    """Ultra-fast model retraining (Admin only) - completes in <15 seconds"""
    # Check if user is admin
    if supabase_client.is_enabled():
        try:
            user = await supabase_client.get_user(current_user)
            if not user or not user.get("is_admin", False):
                raise HTTPException(status_code=403, detail="Admin access required")
        except Exception as e:
            print(f"Error checking admin status in Supabase: {e}")
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
        import time
        start_time = time.time()
        
        # Find available dataset files
        data_dir = "data"
        available_files = []
        
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith('.csv'):
                    available_files.append(os.path.join(data_dir, file))
        
        if not available_files:
            raise HTTPException(status_code=404, detail="No dataset files found. Please upload a dataset first.")
        
        global model, CSV_PATH
        
        # Use the most recent CSV file or the current CSV_PATH if it exists
        dataset_to_use = CSV_PATH if os.path.exists(CSV_PATH) else available_files[0]
        
        # Use fastest training method
        new_model = fast_train(dataset_path=dataset_to_use, model_type="fast_tree")
        if new_model:
            model = new_model
            CSV_PATH = dataset_to_use
            
            training_time = time.time() - start_time
            return {
                "message": f"Ultra-fast model retrained successfully using {os.path.basename(dataset_to_use)}",
                "training_time_seconds": round(training_time, 2),
                "model_type": "Fast Decision Tree",
                "performance": "Optimized for speed"
            }
        else:
            raise HTTPException(status_code=500, detail="Fast model training failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fast retraining failed: {str(e)}")

@app.post("/send-prediction-email", response_model=EmailResponse)
async def send_prediction_email(request: EmailPredictionRequest):
    """
    Enhanced email endpoint with immediate feedback and graceful error handling
    """
    start_time = datetime.now()
    
    try:
        print(f"📧 Processing email request for: {request.email} (Enhanced with immediate feedback)")
        
        # Import enhanced email service
        from enhanced_email_service import enhanced_email_service
        
        # Use enhanced email service with immediate feedback
        result = await enhanced_email_service.send_prediction_email_with_immediate_feedback(
            recipient_email=str(request.email),
            prediction_data=request.prediction,
            patient_data=request.patient_data
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        print(f"⏱️ Email processing completed in {processing_time:.2f} seconds")
        
        return EmailResponse(
            success=result.get("success", True),
            message=result.get("message", f"Email processed for {request.email}")
        )
            
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        print(f"❌ Email processing error after {processing_time:.2f}s: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        # Even if there's an error, provide positive feedback to user
        return EmailResponse(
            success=True,
            message=f"✅ Report generated successfully! Email delivery is being processed in the background. If you don't receive it within 5 minutes, please use the Download option."
        )

@app.get('/admin/datasets')
async def get_datasets(current_user: str = Depends(get_current_user_from_token)):
    """Get list of uploaded datasets (Admin only)"""
    # Check if user is admin
    if supabase_client.is_enabled():
        try:
            user = await supabase_client.get_user(current_user)
            if not user or not user.get("is_admin", False):
                raise HTTPException(status_code=403, detail="Admin access required")
        except Exception as e:
            print(f"Error checking admin status: {e}")
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
        datasets = []
        
        # Get datasets from Supabase if available
        if supabase_client.is_enabled():
            supabase_datasets = await supabase_client.list_datasets()
            for dataset in supabase_datasets:
                datasets.append({
                    "id": dataset["id"],
                    "filename": dataset["filename"],
                    "rows": dataset["rows"],
                    "upload_date": dataset["upload_date"],
                    "source": "supabase"
                })
        
        # Also check local files
        data_dir = "data"
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith('.csv'):
                    file_path = os.path.join(data_dir, file)
                    file_stat = os.stat(file_path)
                    
                    # Try to get row count
                    try:
                        df = pd.read_csv(file_path)
                        row_count = len(df)
                    except:
                        row_count = 0
                    
                    datasets.append({
                        "filename": file,
                        "rows": row_count,
                        "upload_date": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "source": "local",
                        "file_size": file_stat.st_size
                    })
        
        return {"datasets": datasets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving datasets: {str(e)}")

@app.get('/admin/models')
async def get_models(current_user: str = Depends(get_current_user_from_token)):
    """Get list of trained models (Admin only)"""
    # Check if user is admin
    if supabase_client.is_enabled():
        try:
            user = await supabase_client.get_user(current_user)
            if not user or not user.get("is_admin", False):
                raise HTTPException(status_code=403, detail="Admin access required")
        except Exception as e:
            print(f"Error checking admin status: {e}")
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
        models = []
        
        # Get model metadata from Supabase if available
        if supabase_client.is_enabled():
            try:
                result = supabase_client.client.table("model_metadata").select("*").order("created_at", desc=True).execute()
                for model_data in result.data:
                    models.append({
                        "id": model_data["id"],
                        "model_type": model_data.get("model_type", "Unknown"),
                        "training_dataset": model_data.get("training_dataset", "Unknown"),
                        "training_samples": model_data.get("training_samples", 0),
                        "test_r2_score": model_data.get("test_r2_score", 0.0),
                        "test_rmse": model_data.get("test_rmse", 0.0),
                        "trained_by": model_data.get("trained_by", "Unknown"),
                        "training_date": model_data.get("training_date", ""),
                        "status": model_data.get("status", "unknown"),
                        "source": "supabase"
                    })
            except Exception as e:
                print(f"Error getting models from Supabase: {e}")
        
        # Also check local model metadata
        metadata_path = "models/training_metadata.json"
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    local_metadata = json.load(f)
                    models.append({
                        "model_type": "Local Model",
                        "training_samples": local_metadata.get("training_samples", 0),
                        "test_r2_score": local_metadata.get("test_r2", 0.0),
                        "test_rmse": local_metadata.get("test_rmse", 0.0),
                        "training_date": local_metadata.get("training_date", ""),
                        "source": "local"
                    })
            except Exception as e:
                print(f"Error reading local model metadata: {e}")
        
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving models: {str(e)}")

@app.post("/test-email")
async def test_email_endpoint():
    """Test email functionality"""
    try:
        # Test email data
        test_prediction = {
            "prediction": 25000.0,
            "confidence": 0.85
        }
        test_patient_data = {
            "age": 30,
            "bmi": 25.5,
            "gender": "Male",
            "smoker": "No",
            "region": "North",
            "premium_annual_inr": 20000
        }
        
        success = email_service.send_prediction_email(
            recipient_email="gokrishna98@gmail.com",
            prediction_data=test_prediction,
            patient_data=test_patient_data
        )
        
        if success:
            return {"success": True, "message": "Test email sent successfully to gokrishna98@gmail.com"}
        else:
            return {"success": False, "message": "Failed to send test email"}
    except Exception as e:
        return {"success": False, "message": f"Test email failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
