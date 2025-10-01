#!/usr/bin/env python3
"""
Deploy Email Fix to Render
Applies the email functionality fixes to the Render deployment
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_render_backend():
    """Test if Render backend is accessible"""
    
    render_url = "https://srv-d3b668ogjchc73f9ece0.onrender.com"
    
    print("🌐 Testing Render Backend Accessibility")
    print("=" * 50)
    print(f"URL: {render_url}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{render_url}/health", timeout=15)
        
        if response.status_code == 200:
            print("✅ Render backend is accessible")
            return True
        else:
            print(f"⚠️ Render backend returned status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Render backend is starting up (timeout)")
        print("💡 Render services may take 30-60 seconds to wake up")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Render backend")
        return False
    except Exception as e:
        print(f"❌ Error testing Render backend: {e}")
        return False

def test_render_email_functionality():
    """Test email functionality on Render"""
    
    render_url = "https://srv-d3b668ogjchc73f9ece0.onrender.com"
    
    print("\n📧 Testing Email Functionality on Render")
    print("=" * 50)
    
    # Test the problematic email
    test_data = {
        "email": "perivihk@gmail.com",
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
        print(f"📧 Testing email: {test_data['email']}")
        print("🚀 Sending request to Render...")
        
        response = requests.post(
            f"{render_url}/send-prediction-email",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for Render
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            message = result.get('message', 'No message')
            
            print(f"✅ Success: {success}")
            print(f"📝 Message: {message}")
            
            if success:
                print("\n🎉 EMAIL FUNCTIONALITY WORKING ON RENDER!")
                return True
            else:
                print("\n❌ Email sending failed on Render")
                return False
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"📝 Error Text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out")
        print("💡 Render service might be cold starting")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def check_render_environment_status():
    """Check if Render environment variables are properly configured"""
    
    print("\n🔍 Checking Render Environment Configuration")
    print("=" * 50)
    
    # These should be set in Render dashboard
    required_vars = [
        "GMAIL_EMAIL",
        "GMAIL_APP_PASSWORD", 
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    print("📋 Required Environment Variables for Render:")
    for var in required_vars:
        print(f"   - {var}")
    
    print("\n💡 To configure these in Render:")
    print("1. Go to Render Dashboard")
    print("2. Select your backend service")
    print("3. Go to Environment tab")
    print("4. Add each variable with proper values")
    print("5. Redeploy the service")
    
    return True

def create_render_deployment_checklist():
    """Create a checklist for Render deployment"""
    
    checklist = """
# Render Deployment Checklist for Email Fix

## ✅ Pre-deployment Checklist

### 1. Code Changes Applied
- [x] Updated app.py email endpoint logic
- [x] Updated database.py email saving logic  
- [x] Email service handles existing emails properly
- [x] All fixes tested on localhost

### 2. Environment Variables Required
Add these to Render Dashboard > Environment:

```
GMAIL_EMAIL=gokrishna98@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password
SUPABASE_URL=https://gucyzhjyciqnvxedmoxo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

### 3. Gmail App Password Setup
- [ ] Enable 2-Factor Authentication on Gmail
- [ ] Generate App Password: Google Account > Security > 2-Step Verification > App passwords
- [ ] Use 16-character password (no spaces)

## 🚀 Deployment Steps

### 1. Update Environment Variables
- [ ] Go to Render Dashboard
- [ ] Select backend service (srv-d3b668ogjchc73f9ece0)
- [ ] Navigate to Environment tab
- [ ] Add/update all required variables
- [ ] Save changes

### 2. Deploy Updated Code
- [ ] Push code changes to GitHub repository
- [ ] Render will auto-deploy from GitHub
- [ ] Wait for deployment to complete (5-10 minutes)

### 3. Test Deployment
- [ ] Wait for service to start (may take 30-60 seconds)
- [ ] Test health endpoint: GET /health
- [ ] Test email endpoint with existing email: perivihk@gmail.com
- [ ] Verify email is sent successfully

## 🧪 Testing Commands

### Test Render Backend
```bash
curl https://srv-d3b668ogjchc73f9ece0.onrender.com/health
```

### Test Email Functionality
```bash
curl -X POST https://srv-d3b668ogjchc73f9ece0.onrender.com/send-prediction-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "perivihk@gmail.com",
    "prediction": {"prediction": 25000.0, "confidence": 0.85},
    "patient_data": {
      "age": 35, "bmi": 23.0, "gender": "Male", 
      "smoker": "No", "region": "East", "premium_annual_inr": 30000
    }
  }'
```

## 🔧 Troubleshooting

### If Email Fails:
1. Check Render logs for error messages
2. Verify Gmail App Password is correct
3. Ensure all environment variables are set
4. Check Supabase connection

### If Service Won't Start:
1. Check Render build logs
2. Verify all dependencies in requirements.txt
3. Check for Python syntax errors
4. Ensure all imports are available

### If Database Errors:
1. Verify Supabase URL and key
2. Check database tables exist
3. Run database migration if needed

## ✅ Success Criteria

- [ ] Render service starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] Email endpoint accepts existing emails (perivihk@gmail.com)
- [ ] Emails are sent successfully
- [ ] No "email already exists" blocking issues
- [ ] Frontend can send emails through Render backend

## 📞 Support

If issues persist:
1. Check Render service logs
2. Verify environment variables
3. Test with fresh email address
4. Check Gmail account settings
"""
    
    with open("render_deployment_checklist.md", 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print("✅ Created deployment checklist: render_deployment_checklist.md")

def main():
    """Main deployment function"""
    
    print("🚀 Deploy Email Fix to Render")
    print("=" * 60)
    
    # Test Render backend accessibility
    render_accessible = test_render_backend()
    
    if render_accessible:
        # Test email functionality
        email_working = test_render_email_functionality()
        
        if email_working:
            print("\n🎉 EMAIL FIX ALREADY WORKING ON RENDER!")
            print("✅ No additional deployment needed")
        else:
            print("\n⚠️ Email functionality needs fixing on Render")
            print("💡 Follow the deployment checklist")
    else:
        print("\n⚠️ Render backend not accessible")
        print("💡 Service may be sleeping or needs deployment")
    
    # Check environment configuration
    check_render_environment_status()
    
    # Create deployment checklist
    create_render_deployment_checklist()
    
    print("\n📋 DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    if render_accessible:
        print("✅ Render backend is accessible")
    else:
        print("⚠️ Render backend needs to be started/deployed")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Review render_deployment_checklist.md")
    print("2. Update environment variables in Render dashboard")
    print("3. Push code changes to trigger deployment")
    print("4. Test email functionality after deployment")
    print("5. Verify with perivihk@gmail.com email")
    
    print("\n📁 FILES CREATED:")
    print("- render_deployment_checklist.md")
    print("- render_env_template.txt (from previous script)")

if __name__ == "__main__":
    main()
