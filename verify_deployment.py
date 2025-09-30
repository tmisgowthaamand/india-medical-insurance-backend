#!/usr/bin/env python3
"""
Verify deployment readiness for Render
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        "requirements.txt",
        "start.sh", 
        "render.yaml",
        "app.py",
        ".env"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
            print(f"❌ Missing: {file}")
        else:
            print(f"✅ Found: {file}")
    
    return len(missing_files) == 0

def check_requirements():
    """Check requirements.txt for issues"""
    print("\n📦 Checking requirements.txt...")
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        # Check for problematic entries
        lines = content.strip().split('\n')
        issues = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line == 'smtplib':
                issues.append("smtplib is a built-in library and shouldn't be in requirements.txt")
            elif 'supabase==' in line:
                if 'supabase==1.0.3' not in line:
                    issues.append(f"Supabase version should be 1.0.3, found: {line}")
        
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Requirements.txt looks good")
            return True
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n🔧 Checking environment variables...")
    
    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded .env file")
    except Exception as e:
        print(f"⚠️ Could not load .env file: {e}")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY", 
        "JWT_SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ Missing: {var}")
        else:
            print(f"✅ Found: {var} (length: {len(value)})")
    
    return len(missing_vars) == 0

def check_startup_script():
    """Check start.sh script"""
    print("\n🚀 Checking start.sh script...")
    
    try:
        with open("start.sh", "r", encoding='utf-8') as f:
            content = f.read()
        
        # Check for key elements
        checks = [
            ("PORT variable", "PORT=" in content),
            ("uvicorn command", "uvicorn app:app" in content),
            ("Host binding", "--host 0.0.0.0" in content),
            ("Port binding", "--port $PORT" in content)
        ]
        
        all_good = True
        for check_name, condition in checks:
            if condition:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error reading start.sh: {e}")
        return False

def main():
    """Main verification function"""
    print("🏥 MediCare+ Deployment Verification")
    print("=" * 50)
    
    # Change to backend directory if not already there
    if not os.path.exists("app.py"):
        if os.path.exists("backend/app.py"):
            os.chdir("backend")
            print("📂 Changed to backend directory")
        else:
            print("❌ Cannot find app.py. Please run from backend directory.")
            return False
    
    # Run all checks
    files_ok = check_files()
    requirements_ok = check_requirements()
    env_ok = check_environment()
    startup_ok = check_startup_script()
    
    print("\n" + "=" * 50)
    print("📊 Verification Results:")
    print(f"Required Files: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"Requirements.txt: {'✅ PASS' if requirements_ok else '❌ FAIL'}")
    print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Startup Script: {'✅ PASS' if startup_ok else '❌ FAIL'}")
    
    all_passed = all([files_ok, requirements_ok, env_ok, startup_ok])
    
    if all_passed:
        print("\n🎉 All checks passed! Ready for Render deployment.")
        print("\n📋 Next steps:")
        print("1. Commit and push these changes to your repository")
        print("2. Redeploy on Render")
        print("3. Check https://india-medical-insurance-backend.onrender.com/health")
    else:
        print("\n⚠️ Some checks failed. Please fix the issues above before deploying.")
    
    return all_passed

if __name__ == "__main__":
    main()
