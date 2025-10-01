#!/usr/bin/env python3
"""
Clean Deployment Fix for Render Backend
No emojis - Windows compatible
"""

import os
import sys
import subprocess
from pathlib import Path

def create_startup_script():
    """Create a startup script for Render"""
    print("Creating startup script...")
    
    startup_content = """#!/bin/bash
# Render startup script for MediCare+ Backend

echo "Starting MediCare+ Backend..."
echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Installing dependencies..."
    pip install -r requirements-render.txt
fi

# Start the application
echo "Starting FastAPI server..."
exec uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1
"""
    
    try:
        with open("start.sh", "w", encoding='utf-8') as f:
            f.write(startup_content)
        print("SUCCESS: Created start.sh")
        return True
    except Exception as e:
        print(f"ERROR: Creating startup script failed: {e}")
        return False

def update_app_for_production():
    """Update app.py for better production compatibility"""
    print("Updating app.py for production...")
    
    try:
        # Read current app.py
        with open("app.py", "r", encoding='utf-8') as f:
            content = f.read()
        
        # Add health check if not present
        if "/health" not in content:
            health_check = '''
@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "service": "MediCare+ Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
'''
            # Add import for datetime if not present
            if "from datetime import datetime" not in content:
                content = "from datetime import datetime\n" + content
            
            # Add health check before the main block
            content = content.replace(
                'if __name__ == "__main__":',
                health_check + '\nif __name__ == "__main__":'
            )
            
            with open("app.py", "w", encoding='utf-8') as f:
                f.write(content)
            
            print("SUCCESS: Added health check endpoint")
        else:
            print("SUCCESS: Health check already exists")
        
        return True
    except Exception as e:
        print(f"ERROR: Updating app.py failed: {e}")
        return False

def create_render_build_script():
    """Create build script for Render"""
    print("Creating build script...")
    
    build_content = """#!/bin/bash
# Render build script

echo "Building MediCare+ Backend..."

# Install Python dependencies
pip install -r requirements-render.txt

# Create necessary directories
mkdir -p models
mkdir -p data
mkdir -p logs

echo "Build completed successfully"
"""
    
    try:
        with open("build.sh", "w", encoding='utf-8') as f:
            f.write(build_content)
        print("SUCCESS: Created build.sh")
        return True
    except Exception as e:
        print(f"ERROR: Creating build script failed: {e}")
        return False

def verify_essential_files():
    """Verify all essential files are present"""
    print("Verifying essential files...")
    
    essential_files = [
        "app.py",
        "requirements-render.txt", 
        "Procfile",
        "render.yaml"
    ]
    
    missing_files = []
    for file in essential_files:
        if not os.path.exists(file):
            missing_files.append(file)
            print(f"MISSING: {file}")
        else:
            print(f"SUCCESS: {file} found")
    
    if missing_files:
        print(f"ERROR: Missing files: {missing_files}")
        return False
    
    print("SUCCESS: All essential files present")
    return True

def create_environment_template():
    """Create environment template for Render"""
    print("Creating environment template...")
    
    env_template = """# Environment Variables for Render Dashboard
# Copy these to your Render service environment variables

SUPABASE_URL=https://gucyzhjyciqnvxedmoxo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODA0MTksImV4cCI6MjA3NDQ1NjQxOX0.BYbV3CHVTrd4KzhRAFSYB7S2RiFv342f0J-Es-4pkKI
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4
JWT_SECRET_KEY=medical_insurance_dashboard_jwt_secret_key_2024_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
ALLOWED_ORIGINS=https://india-medical-insurance-frontend.vercel.app,*
"""
    
    try:
        with open("render_env_template.txt", "w", encoding='utf-8') as f:
            f.write(env_template)
        print("SUCCESS: Created render_env_template.txt")
        return True
    except Exception as e:
        print(f"ERROR: Creating environment template failed: {e}")
        return False

def main():
    """Main deployment fix function"""
    print("=" * 60)
    print("Clean Deployment Fix for Render Backend")
    print("=" * 60)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Create startup script
    if create_startup_script():
        success_count += 1
    
    # Step 2: Update app.py
    if update_app_for_production():
        success_count += 1
    
    # Step 3: Create build script
    if create_render_build_script():
        success_count += 1
    
    # Step 4: Verify files
    if verify_essential_files():
        success_count += 1
    
    # Step 5: Create environment template
    if create_environment_template():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {success_count}/{total_steps} steps completed successfully")
    
    if success_count == total_steps:
        print("\nSUCCESS: Deployment preparation completed!")
        print("\nDEPLOYMENT INSTRUCTIONS:")
        print("1. Push all changes to your Git repository")
        print("2. In Render Dashboard:")
        print("   - Build Command: pip install -r requirements-render.txt")
        print("   - Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT")
        print("3. Add environment variables from render_env_template.txt")
        print("4. Deploy and test")
        print("\nTEST URLS:")
        print("   - Health: https://your-app.onrender.com/health")
        print("   - API Docs: https://your-app.onrender.com/docs")
        print("   - Prediction: https://your-app.onrender.com/predict")
        
        return True
    else:
        print("\nERROR: Some steps failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
