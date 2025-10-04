#!/usr/bin/env python3
"""
Deployment Script to Fix Email Functionality on Render
"""

import os
import sys
import subprocess
import json

def check_environment_variables():
    """Check if required environment variables are set"""
    print("🔍 Checking Environment Variables")
    print("=" * 50)
    
    required_vars = [
        "GMAIL_EMAIL",
        "GMAIL_APP_PASSWORD",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == "GMAIL_APP_PASSWORD":
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value[:50]}{'...' if len(value) > 50 else ''}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def create_render_env_file():
    """Create a .env file for Render deployment"""
    print("\n📝 Creating .env file for Render")
    print("=" * 50)
    
    env_content = """# Render Environment Variables for MediCare+ Email Functionality

# Gmail Configuration (Required for email functionality)
GMAIL_EMAIL=gokrishna98@gmail.com
GMAIL_APP_PASSWORD=lwkvzupqanxvafrm

# Supabase Configuration
SUPABASE_URL=https://gucyzhjyciqnvxedmoxo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4

# CORS Configuration
ALLOWED_ORIGINS=https://india-medical-insurance-frontend.vercel.app,http://localhost:3000,http://localhost:3001

# JWT Configuration
JWT_SECRET_KEY=medical_insurance_dashboard_jwt_secret_key_2024_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
"""
    
    with open(".env.render", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env.render file")
    print("💡 IMPORTANT: Update the values in .env.render with your actual credentials")
    print("💡 Then add these as environment variables in your Render dashboard")

def update_render_yaml():
    """Update render.yaml with email environment variables"""
    print("\n🔧 Updating render.yaml")
    print("=" * 50)
    
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "medical-insurance-api",
                "env": "python",
                "plan": "free",
                "buildCommand": "pip install -r requirements-render.txt",
                "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1",
                "envVars": [
                    {"key": "PYTHON_VERSION", "value": "3.11.0"},
                    {"key": "SUPABASE_URL", "value": "https://gucyzhjyciqnvxedmoxo.supabase.co"},
                    {"key": "SUPABASE_ANON_KEY", "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODA0MTksImV4cCI6MjA3NDQ1NjQxOX0.BYbV3CHVTrd4KzhRAFSYB7S2RiFv342f0J-Es-4pkKI"},
                    {"key": "SUPABASE_SERVICE_ROLE_KEY", "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4"},
                    {"key": "JWT_SECRET_KEY", "value": "medical_insurance_dashboard_jwt_secret_key_2024_change_in_production"},
                    {"key": "JWT_ALGORITHM", "value": "HS256"},
                    {"key": "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "value": "30"},
                    {"key": "ENVIRONMENT", "value": "production"},
                    {"key": "ALLOWED_ORIGINS", "value": "https://india-medical-insurance-frontend.vercel.app,http://localhost:3000,*"},
                    {"key": "GMAIL_EMAIL", "value": "gokrishna98@gmail.com"},
                    {"key": "GMAIL_APP_PASSWORD", "value": "lwkvzupqanxvafrm"}
                ],
                "healthCheckPath": "/health"
            }
        ]
    }
    
    with open("render.yaml", "w") as f:
        yaml_content = """services:
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
      - key: GMAIL_EMAIL
        value: gokrishna98@gmail.com
      - key: GMAIL_APP_PASSWORD
        value: lwkvzupqanxvafrm
    healthCheckPath: /health
"""
        f.write(yaml_content)
    
    print("✅ Updated render.yaml with Gmail environment variables")

def show_deployment_instructions():
    """Show deployment instructions"""
    print("\n🚀 DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    print("1. Update render.yaml with your actual Gmail credentials")
    print("2. Deploy to Render using the dashboard or CLI:")
    print("   render deploy")
    print("3. In Render Dashboard:")
    print("   - Go to your service settings")
    print("   - Add these environment variables:")
    print("     * GMAIL_EMAIL: your-gmail@gmail.com")
    print("     * GMAIL_APP_PASSWORD: your-16-character-app-password")
    print("4. Redeploy your service")
    print("5. Test email functionality")

def main():
    """Main function"""
    print("📧 RENDER EMAIL FIX DEPLOYMENT SCRIPT")
    print("=" * 60)
    
    # Check current environment
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n⚠️  Missing environment variables detected")
        create_render_env_file()
        update_render_yaml()
        show_deployment_instructions()
    else:
        print("\n✅ All required environment variables are set")
        print("💡 You can deploy to Render now")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Review the updated render.yaml")
    print("2. Deploy to Render")
    print("3. Test email functionality with /test-email endpoint")

if __name__ == "__main__":
    main()
