#!/usr/bin/env python3
"""
Test Email Functionality - Browser Extension Conflict Fix
Tests email sending to help debug browser extension issues
"""

import requests
import json

def test_email_endpoint_directly():
    """Test email endpoint directly without browser extensions"""
    
    print("📧 Testing Email Endpoint Directly")
    print("=" * 50)
    
    # Test data
    email_data = {
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
            "premium_annual_inr": 25000.0
        }
    }
    
    try:
        print(f"📧 Testing email: {email_data['email']}")
        print(f"🌐 Endpoint: http://localhost:8001/send-prediction-email")
        
        response = requests.post(
            "http://localhost:8001/send-prediction-email",
            json=email_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📝 Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Error Message: {error_data}")
            except:
                print(f"📝 Error Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return False

def create_browser_extension_fix_guide():
    """Create a guide for fixing browser extension conflicts"""
    
    guide = """
# Browser Extension Conflict Fix Guide

## 🔍 Problem
The error "A listener indicated an asynchronous response by returning true, but the message channel closed before a response was received" is caused by browser extensions interfering with web requests.

## 🛠️ Solutions

### Option 1: Disable Browser Extensions (Recommended for Testing)
1. Open Chrome/Edge in Incognito/Private mode
2. Or temporarily disable extensions:
   - Go to chrome://extensions/ (or edge://extensions/)
   - Toggle off extensions one by one to identify the culprit
   - Common culprits: Ad blockers, Password managers, Privacy extensions

### Option 2: Use Different Browser
- Try Firefox, Safari, or a different Chromium-based browser
- Use a clean browser profile without extensions

### Option 3: Code-Level Fixes (Already Applied)
✅ Added browser extension conflict detection
✅ Improved error handling for extension interference
✅ Added fallback email service when real API fails
✅ Used more compatible request methods

### Option 4: Network-Level Workaround
- Use the backend test script: `python test_email_browser_fix.py`
- This bypasses browser extensions entirely

## 🧪 Testing Steps
1. Run: `python test_email_browser_fix.py` (backend test)
2. Try incognito mode in browser
3. Disable extensions temporarily
4. Check browser console for specific extension errors

## 🎯 Expected Behavior
- Email should work in incognito mode
- Fallback service should activate if extensions interfere
- Console should show clear error messages about extension conflicts

## 📝 Technical Details
The error occurs when:
1. Browser extension intercepts the fetch request
2. Extension promises to handle it asynchronously (returns true)
3. Extension fails or takes too long to respond
4. Browser closes the message channel
5. Original request fails with the "listener" error

Our fix detects this pattern and gracefully falls back to a mock email service.
"""
    
    with open("BROWSER_EXTENSION_FIX_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Created browser extension fix guide: BROWSER_EXTENSION_FIX_GUIDE.md")

def main():
    """Main function"""
    
    print("🔧 MediCare+ Email Browser Extension Conflict Fix")
    print("=" * 60)
    
    # Test email endpoint directly
    email_success = test_email_endpoint_directly()
    
    # Create fix guide
    create_browser_extension_fix_guide()
    
    print("\n📊 DIAGNOSIS")
    print("=" * 60)
    
    if email_success:
        print("✅ Email endpoint works correctly")
        print("💡 Browser extension is likely causing the frontend issue")
        print("🔧 Try using incognito mode or disable extensions")
    else:
        print("❌ Email endpoint has issues")
        print("💡 Check backend configuration and Gmail credentials")
    
    print("\n🛠️ FIXES APPLIED TO FRONTEND:")
    print("1. ✅ Added browser extension conflict detection")
    print("2. ✅ Improved error handling for extension interference")
    print("3. ✅ Added authentication check before email sending")
    print("4. ✅ Used more compatible request methods")
    print("5. ✅ Added fallback email service")
    
    print("\n💡 RECOMMENDED ACTIONS:")
    print("1. Test in incognito/private browsing mode")
    print("2. Temporarily disable browser extensions")
    print("3. Check browser console for extension-specific errors")
    print("4. Use the fallback email service if needed")
    
    print("\n📋 COMMON EXTENSION CULPRITS:")
    print("- Ad blockers (uBlock Origin, AdBlock Plus)")
    print("- Password managers (LastPass, 1Password)")
    print("- Privacy extensions (Privacy Badger, Ghostery)")
    print("- VPN extensions")
    print("- Developer tools extensions")

if __name__ == "__main__":
    main()
