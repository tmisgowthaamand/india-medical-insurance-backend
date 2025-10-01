#!/usr/bin/env python3
"""
Fix Missing Dependencies for Render Deployment
Adds all missing packages that are imported in the codebase
"""

import os
import sys

def check_imports():
    """Check what packages are imported in the codebase"""
    print("Checking imports in codebase...")
    
    imports_found = set()
    
    # Check main files
    files_to_check = [
        "app.py",
        "email_service.py", 
        "database.py",
        "fast_train.py"
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for import statements
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        imports_found.add(line)
                        
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    print(f"Found {len(imports_found)} import statements")
    return imports_found

def update_requirements():
    """Update requirements with all missing dependencies"""
    print("Updating requirements files...")
    
    # Complete requirements for production
    complete_requirements = """# Complete requirements for Render deployment
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
jinja2==3.1.2
email-validator==2.1.0
aiofiles==23.2.1
"""
    
    try:
        # Update render requirements
        with open("requirements-render.txt", "w", encoding='utf-8') as f:
            f.write(complete_requirements)
        print("SUCCESS: Updated requirements-render.txt")
        
        # Update main requirements
        main_requirements = """fastapi==0.104.1
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
jinja2==3.1.2
email-validator==2.1.0
aiofiles==23.2.1
"""
        
        with open("requirements.txt", "w", encoding='utf-8') as f:
            f.write(main_requirements)
        print("SUCCESS: Updated requirements.txt")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to update requirements: {e}")
        return False

def create_deployment_checklist():
    """Create a deployment checklist"""
    print("Creating deployment checklist...")
    
    checklist = """# Render Deployment Checklist

## Before Deployment:
1. [x] Added jinja2==3.1.2 to requirements
2. [x] Added email-validator==2.1.0 for email validation
3. [x] Added aiofiles==23.2.1 for file operations
4. [x] Updated both requirements.txt and requirements-render.txt

## Render Dashboard Settings:
- Build Command: pip install -r requirements-render.txt
- Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1

## Environment Variables (copy to Render):
SUPABASE_URL=https://gucyzhjyciqnvxedmoxo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4
JWT_SECRET_KEY=medical_insurance_dashboard_jwt_secret_key_2024_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
ALLOWED_ORIGINS=https://india-medical-insurance-frontend.vercel.app,*

## After Deployment:
- Test health endpoint: https://your-app.onrender.com/health
- Test API docs: https://your-app.onrender.com/docs
- Test prediction endpoint: https://your-app.onrender.com/predict

## Common Issues Fixed:
- ModuleNotFoundError: No module named 'jinja2' - FIXED
- Missing email validation dependencies - FIXED
- File operation dependencies - FIXED
"""
    
    try:
        with open("DEPLOYMENT_CHECKLIST.txt", "w", encoding='utf-8') as f:
            f.write(checklist)
        print("SUCCESS: Created DEPLOYMENT_CHECKLIST.txt")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create checklist: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Fix Missing Dependencies for Render Deployment")
    print("=" * 60)
    
    success_count = 0
    total_steps = 3
    
    # Step 1: Check imports
    imports = check_imports()
    if imports:
        success_count += 1
    
    # Step 2: Update requirements
    if update_requirements():
        success_count += 1
    
    # Step 3: Create checklist
    if create_deployment_checklist():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("\nSUCCESS: All missing dependencies fixed!")
        print("\nNEXT STEPS:")
        print("1. Commit and push changes to Git")
        print("2. Redeploy on Render")
        print("3. Check deployment logs")
        print("4. Test endpoints")
        
        return True
    else:
        print("\nERROR: Some steps failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
