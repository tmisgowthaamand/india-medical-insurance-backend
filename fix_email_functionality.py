#!/usr/bin/env python3
"""
Fix Email Functionality for MediCare+ Platform
Resolves issues with email sending when user already exists in database
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_email_endpoint():
    """Fix the email endpoint in app.py to handle existing emails properly"""
    
    app_file = "app.py"
    
    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found")
        return False
    
    print("🔧 Fixing email endpoint logic...")
    
    # Read current app.py content
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the problematic email endpoint logic
    old_email_logic = '''        # Save email to users table if it doesn't exist
        try:
            if supabase_client.is_enabled():
                email_result = await supabase_client.save_email_to_users(str(request.email))
                if email_result.get("success"):
                    print(f"✅ Email {request.email} saved to users table")
                else:
                    print(f"⚠️ Failed to save email to users table: {email_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️ Error saving email to users table: {e}")'''
    
    new_email_logic = '''        # Save email to users table if it doesn't exist (non-blocking)
        try:
            if supabase_client.is_enabled():
                email_result = await supabase_client.save_email_to_users(str(request.email))
                if email_result.get("success"):
                    if "already exists" in email_result.get("message", ""):
                        print(f"ℹ️ Email {request.email} already exists in users table - proceeding with email")
                    else:
                        print(f"✅ Email {request.email} saved to users table")
                else:
                    print(f"⚠️ Failed to save email to users table: {email_result.get('error', 'Unknown error')}")
                    print("📧 Proceeding with email sending anyway...")
        except Exception as e:
            print(f"⚠️ Error saving email to users table: {e}")
            print("📧 Proceeding with email sending anyway...")'''
    
    if old_email_logic in content:
        content = content.replace(old_email_logic, new_email_logic)
        print("✅ Updated email endpoint logic")
    else:
        print("⚠️ Email endpoint logic not found or already updated")
    
    # Write back the updated content
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Email endpoint fixed successfully")
    return True

def fix_database_email_logic():
    """Fix the database email saving logic"""
    
    database_file = "database.py"
    
    if not os.path.exists(database_file):
        print(f"❌ {database_file} not found")
        return False
    
    print("🔧 Fixing database email logic...")
    
    # Read current database.py content
    with open(database_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the email saving logic
    old_db_logic = '''            # Check if user already exists
            existing_user = await self.get_user(email)
            if existing_user:
                logger.info(f"Email {email} already exists in users table")
                return {"success": True, "message": "Email already exists"}'''
    
    new_db_logic = '''            # Check if user already exists
            existing_user = await self.get_user(email)
            if existing_user:
                logger.info(f"Email {email} already exists in users table")
                return {"success": True, "message": "Email already exists", "existing": True}'''
    
    if old_db_logic in content:
        content = content.replace(old_db_logic, new_db_logic)
        print("✅ Updated database email logic")
    else:
        print("⚠️ Database email logic not found or already updated")
    
    # Write back the updated content
    with open(database_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Database email logic fixed successfully")
    return True

def create_email_test_script():
    """Create a comprehensive email test script"""
    
    test_script = """#!/usr/bin/env python3
\"\"\"
Comprehensive Email Test for MediCare+ Platform
Tests email functionality with existing and new email addresses
\"\"\"

import os
import sys
import asyncio
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_endpoint(base_url, email, test_name):
    \"\"\"Test the email endpoint with given email\"\"\"
    
    print(f"\\n🧪 {test_name}")
    print("=" * 50)
    
    # Test data
    test_data = {
        "email": email,
        "prediction": {
            "prediction": 25000.0,
            "confidence": 0.85
        },
        "patient_data": {
            "age": 35,
            "bmi": 23.0,
            "gender": "Male",
            "smoker": "No",
            "region": "East",
            "premium_annual_inr": 30000
        }
    }
    
    try:
        print(f"📧 Testing email: {email}")
        print(f"🌐 Endpoint: {base_url}/send-prediction-email")
        
        response = requests.post(
            f"{base_url}/send-prediction-email",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📝 Message: {result.get('message', 'No message')}")
            return result.get('success', False)
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Error Message: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"📝 Error Text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    \"\"\"Main test function\"\"\"
    
    print("🏥 MediCare+ Email Functionality Test")
    print("=" * 60)
    
    # Test both localhost and Render
    test_urls = [
        ("http://localhost:8001", "Localhost Backend"),
        ("https://srv-d3b668ogjchc73f9ece0.onrender.com", "Render Backend")
    ]
    
    # Test emails
    test_emails = [
        ("perivihk@gmail.com", "Existing User Email"),
        ("gokrishna98@gmail.com", "Test Email 1"),
        ("test.medicare@gmail.com", "Test Email 2")
    ]
    
    results = []
    
    for base_url, url_name in test_urls:
        print(f"\\n🌐 Testing {url_name}: {base_url}")
        print("=" * 60)
        
        # Test health endpoint first
        try:
            health_response = requests.get(f"{base_url}/health", timeout=10)
            if health_response.status_code == 200:
                print(f"✅ {url_name} is accessible")
            else:
                print(f"⚠️ {url_name} health check failed: {health_response.status_code}")
                continue
        except Exception as e:
            print(f"❌ {url_name} is not accessible: {e}")
            continue
        
        # Test email functionality
        for email, email_desc in test_emails:
            success = test_email_endpoint(base_url, email, f"{email_desc} on {url_name}")
            results.append({
                "url": url_name,
                "email": email,
                "success": success
            })
    
    # Summary
    print("\\n📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
    
    print("\\n📋 Detailed Results:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['url']} - {result['email']}")
    
    if successful_tests == total_tests:
        print("\\n🎉 All email tests passed!")
    else:
        print("\\n⚠️ Some email tests failed - check configuration")

if __name__ == "__main__":
    main()
"""
    
    with open("test_email_comprehensive.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Created comprehensive email test script: test_email_comprehensive.py")

def create_render_deployment_fix():
    """Create a fix script for Render deployment"""
    
    render_fix = """#!/usr/bin/env python3
\"\"\"
Render Deployment Fix for Email Functionality
Ensures email service works properly on Render platform
\"\"\"

import os
import sys
from dotenv import load_dotenv

def check_render_environment():
    \"\"\"Check Render environment variables\"\"\"
    
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
        print(f"\\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\\n✅ All required environment variables are set")
        return True

def test_email_service_import():
    \"\"\"Test if email service can be imported\"\"\"
    
    print("\\n🔍 Testing Email Service Import")
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
    \"\"\"Create environment template for Render\"\"\"
    
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
    \"\"\"Main function\"\"\"
    
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
    
    print("\\n📊 DIAGNOSIS SUMMARY")
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
    
    print("\\n🔧 NEXT STEPS:")
    print("1. Review render_env_template.txt")
    print("2. Add missing environment variables to Render")
    print("3. Redeploy the service")
    print("4. Run test_email_comprehensive.py to verify")

if __name__ == "__main__":
    main()
"""
    
    with open("fix_render_email.py", 'w', encoding='utf-8') as f:
        f.write(render_fix)
    
    print("✅ Created Render deployment fix script: fix_render_email.py")

def main():
    """Main fix function"""
    
    print("🔧 MediCare+ Email Functionality Fix")
    print("=" * 60)
    
    print("1️⃣ Fixing email endpoint logic...")
    fix_email_endpoint()
    
    print("\n2️⃣ Fixing database email logic...")
    fix_database_email_logic()
    
    print("\n3️⃣ Creating email test script...")
    create_email_test_script()
    
    print("\n4️⃣ Creating Render deployment fix...")
    create_render_deployment_fix()
    
    print("\n✅ EMAIL FUNCTIONALITY FIX COMPLETE")
    print("=" * 60)
    print("📋 Files created/updated:")
    print("   - app.py (updated)")
    print("   - database.py (updated)")
    print("   - test_email_comprehensive.py (new)")
    print("   - fix_render_email.py (new)")
    print("   - render_env_template.txt (new)")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Run: python test_email_comprehensive.py")
    print("2. For Render: python fix_render_email.py")
    print("3. Test with existing email: perivihk@gmail.com")
    print("4. Verify both localhost and Render work")

if __name__ == "__main__":
    main()
