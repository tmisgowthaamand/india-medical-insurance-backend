#!/usr/bin/env python3
"""
Comprehensive Render Deployment Fix for MediCare+ Backend
Fixes monotonic_cst error and deployment compatibility issues
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_environment():
    """Check current environment and dependencies"""
    print("🔍 Checking Environment...")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found. Please run from backend directory.")
        return False
    
    print("✅ Environment check passed")
    return True

def fix_requirements():
    """Fix requirements files for compatibility"""
    print("\n📝 Fixing Requirements Files...")
    print("=" * 50)
    
    # Update main requirements.txt
    requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pandas==2.1.4
scikit-learn>=1.3.0,<1.6.0
joblib==1.3.2
numpy==1.24.4
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
supabase==2.0.2
pydantic==2.5.0
PyJWT==2.8.0
"""
    
    # Update render requirements
    render_requirements_content = """# Production requirements for Render deployment - Compatible versions
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pandas==2.1.4
scikit-learn>=1.3.0,<1.6.0
joblib==1.3.2
passlib[bcrypt]==1.7.4
pyjwt==2.8.0
python-multipart==0.0.6
numpy==1.24.4
scipy>=1.11.0
python-jose[cryptography]==3.3.0
bcrypt==4.0.1
cryptography>=3.4.0
python-dateutil>=2.8.2
pytz>=2020.1
tzdata>=2022.1
supabase==2.0.2
python-dotenv==1.0.0
"""
    
    try:
        with open("requirements.txt", "w") as f:
            f.write(requirements_content)
        print("✅ Updated requirements.txt")
        
        with open("requirements-render.txt", "w") as f:
            f.write(render_requirements_content)
        print("✅ Updated requirements-render.txt")
        
        return True
    except Exception as e:
        print(f"❌ Error updating requirements: {e}")
        return False

def retrain_model():
    """Retrain model with compatible parameters"""
    print("\n🤖 Retraining Model...")
    print("=" * 50)
    
    try:
        # Import and run fast training
        from fast_train import fast_train
        
        # Check for dataset
        data_dir = "data"
        if not os.path.exists(data_dir):
            print("❌ Data directory not found")
            return False
        
        dataset_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if not dataset_files:
            print("❌ No CSV dataset files found")
            return False
        
        dataset_path = os.path.join(data_dir, dataset_files[0])
        print(f"📊 Using dataset: {dataset_path}")
        
        # Retrain with compatible model
        model = fast_train(dataset_path=dataset_path, model_type="fast_rf")
        
        if model:
            print("✅ Model retrained successfully")
            return True
        else:
            print("❌ Model retraining failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during model retraining: {e}")
        return False

def create_render_config():
    """Create optimized render.yaml configuration"""
    print("\n⚙️ Creating Render Configuration...")
    print("=" * 50)
    
    render_config = """services:
  - type: web
    name: medical-insurance-api
    env: python
    plan: free
    buildCommand: pip install -r requirements-render.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SUPABASE_URL
        value: https://gucyzhjyciqnvxedmoxo.supabase.co
      - key: SUPABASE_ANON_KEY
        value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODA0MTksImV4cCI6MjA3NDQ1NjQxOX0.BYbV3CHVTrd4KzhRAFSYB7S2RiFv342f0J-Es-4pkKI
      - key: SUPABASE_SERVICE_ROLE_KEY
        value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4
      - key: JWT_SECRET_KEY
        value: medical_insurance_dashboard_jwt_secret_key_2024_change_in_production
      - key: JWT_ALGORITHM
        value: HS256
      - key: JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        value: 30
      - key: ENVIRONMENT
        value: production
      - key: ALLOWED_ORIGINS
        value: https://india-medical-insurance-frontend.vercel.app,http://localhost:3000,*
    healthCheckPath: /health
"""
    
    try:
        with open("render.yaml", "w") as f:
            f.write(render_config)
        print("✅ Created optimized render.yaml")
        return True
    except Exception as e:
        print(f"❌ Error creating render.yaml: {e}")
        return False

def create_procfile():
    """Create Procfile for deployment"""
    print("\n📄 Creating Procfile...")
    print("=" * 50)
    
    procfile_content = "web: uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1"
    
    try:
        with open("Procfile", "w") as f:
            f.write(procfile_content)
        print("✅ Created Procfile")
        return True
    except Exception as e:
        print(f"❌ Error creating Procfile: {e}")
        return False

def test_compatibility():
    """Test model and deployment compatibility"""
    print("\n🧪 Testing Compatibility...")
    print("=" * 50)
    
    try:
        # Test model loading
        from joblib import load
        import pandas as pd
        
        model_path = "models/model_pipeline.pkl"
        if os.path.exists(model_path):
            model = load(model_path)
            
            # Test prediction
            test_data = pd.DataFrame({
                'age': [30],
                'bmi': [25.0],
                'gender': ['Male'],
                'smoker': ['No'],
                'region': ['North'],
                'premium_annual_inr': [15000.0]
            })
            
            prediction = model.predict(test_data)
            print(f"✅ Test prediction successful: ₹{prediction[0]:.2f}")
            
        # Test imports
        import fastapi
        import uvicorn
        import pandas
        import sklearn
        import joblib
        import numpy
        
        print("✅ All imports successful")
        print(f"   - FastAPI: {fastapi.__version__}")
        print(f"   - Scikit-learn: {sklearn.__version__}")
        print(f"   - Pandas: {pandas.__version__}")
        print(f"   - NumPy: {numpy.__version__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
        return False

def main():
    """Main deployment fix function"""
    print("🚀 Render Deployment Fix for MediCare+ Backend")
    print("=" * 60)
    
    success_count = 0
    total_steps = 6
    
    # Step 1: Environment check
    if check_environment():
        success_count += 1
    
    # Step 2: Fix requirements
    if fix_requirements():
        success_count += 1
    
    # Step 3: Retrain model
    if retrain_model():
        success_count += 1
    
    # Step 4: Create render config
    if create_render_config():
        success_count += 1
    
    # Step 5: Create Procfile
    if create_procfile():
        success_count += 1
    
    # Step 6: Test compatibility
    if test_compatibility():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {success_count}/{total_steps} steps completed successfully")
    
    if success_count == total_steps:
        print("\n🎉 SUCCESS! Render deployment is ready!")
        print("\n📋 Next Steps:")
        print("1. Commit and push changes to your repository")
        print("2. Deploy to Render using the updated configuration")
        print("3. Test the deployed endpoints")
        print("\n🔗 Key URLs after deployment:")
        print("   - API Docs: https://your-app.onrender.com/docs")
        print("   - Health Check: https://your-app.onrender.com/health")
        print("   - Prediction: https://your-app.onrender.com/predict")
        
        return True
    else:
        print("\n❌ Some steps failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
