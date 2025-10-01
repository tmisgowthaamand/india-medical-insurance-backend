#!/usr/bin/env python3
"""
Render Deployment Fix for Email Functionality
Ensures email service works properly on Render platform
"""

import os
import sys
from dotenv import load_dotenv

def check_render_environment():
    """Check Render environment variables"""
    
    print("🔍 Checking Render Environment Variables")
    print("=" * 50)
    
    required_vars = [
        "GMAIL_EMAIL",
        "GMAIL_APP_PASSWORD",
        "SUPABASE_URL", 
        "SUPABASE_SERVICE_ROLE_KEY",
        "ALLOWED_ORIGINS"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == "GMAIL_APP_PASSWORD":
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All required environment variables are set")
        return True

def test_email_service_import():
    """Test if email service can be imported"""
    
    print("\n🔍 Testing Email Service Import")
    print("=" * 50)
    
    try:
        from email_service import email_service
        print("✅ Email service imported successfully")
        
        if email_service.is_email_enabled():
            print("✅ Email service is enabled")
            return True
        else:
            print("❌ Email service is disabled")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import email service: {e}")
        return False
    except Exception as e:
        print(f"❌ Error with email service: {e}")
        return False

def create_render_env_template():
    """Create environment template for Render"""
    
    env_template = '''# Render Environment Variables Template for MediCare+ Email Functionality

# Gmail Configuration (Required for email functionality)
GMAIL_EMAIL=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# CORS Configuration
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000,http://localhost:3001

# Instructions:
# 1. Replace all placeholder values with your actual credentials
# 2. Add these as environment variables in Render dashboard
# 3. Redeploy your service after adding variables
# 4. Test email functionality using the test script

# Gmail App Password Setup:
# 1. Go to Google Account settings
# 2. Enable 2-Factor Authentication
# 3. Go to Security > 2-Step Verification > App passwords
# 4. Generate app password for "Mail"
# 5. Use the 16-character password (no spaces)
'''
    
    with open("render_env_template.txt", 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print("✅ Created Render environment template: render_env_template.txt")

def main():
    """Main function"""
    
    print("🚀 Render Deployment Fix for Email Functionality")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment
    env_ok = check_render_environment()
    
    # Test email service
    service_ok = test_email_service_import()
    
    # Create templates
    create_render_env_template()
    
    print("\n📊 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if env_ok and service_ok:
        print("✅ Email functionality should work on Render")
        print("💡 If still having issues, check Gmail App Password configuration")
    elif not env_ok:
        print("❌ Environment variables missing")
        print("💡 Add missing variables to Render dashboard and redeploy")
    elif not service_ok:
        print("❌ Email service configuration issue")
        print("💡 Check Gmail credentials and app password")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Review render_env_template.txt")
    print("2. Add missing environment variables to Render")
    print("3. Redeploy the service")
    print("4. Run test_email_comprehensive.py to verify")

if __name__ == "__main__":
    main()
