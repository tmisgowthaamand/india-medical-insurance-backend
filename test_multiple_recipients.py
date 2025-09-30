#!/usr/bin/env python3
"""
Test Multiple Email Recipients
Verify that emails can be sent to different Gmail addresses
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_multiple_recipients():
    """Test sending emails to multiple different recipients"""
    print("📧 TESTING MULTIPLE EMAIL RECIPIENTS")
    print("=" * 60)
    
    try:
        from email_service import email_service
        
        # Test prediction data
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
        
        # Test different recipient emails
        test_recipients = [
            "gokrishna98@gmail.com",  # Original sender email
            # Add more test emails here if you have them
        ]
        
        print("📋 Available test recipients:")
        for i, email in enumerate(test_recipients, 1):
            print(f"   {i}. {email}")
        
        # Get recipient email from user
        recipient_email = input(f"\n📧 Enter recipient email to test (or press Enter for {test_recipients[0]}): ").strip()
        if not recipient_email:
            recipient_email = test_recipients[0]
        
        print(f"\n📧 Sending test email to: {recipient_email}")
        print(f"📤 From: {email_service.sender_email}")
        print("-" * 50)
        
        # Send email
        success = email_service.send_prediction_email(
            recipient_email=recipient_email,
            prediction_data=test_prediction,
            patient_data=test_patient_data
        )
        
        if success:
            print(f"✅ Email sent successfully to {recipient_email}")
            print("\n📱 CHECK EMAIL:")
            print(f"   1. Check inbox for: {recipient_email}")
            print("   2. Check spam/junk folder")
            print("   3. Check promotions tab (Gmail)")
            print("   4. Wait 1-2 minutes for delivery")
            return True
        else:
            print(f"❌ Failed to send email to {recipient_email}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_email_validation():
    """Test email validation for different formats"""
    print("\n🔍 TESTING EMAIL VALIDATION")
    print("=" * 50)
    
    test_emails = [
        ("valid@gmail.com", True),
        ("test.email@yahoo.com", True),
        ("user123@hotmail.com", True),
        ("invalid-email", False),
        ("@gmail.com", False),
        ("test@", False),
        ("", False)
    ]
    
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    all_passed = True
    for email, should_be_valid in test_emails:
        is_valid = bool(re.match(email_pattern, email))
        status = "✅" if is_valid == should_be_valid else "❌"
        print(f"{status} {email:<20} - {'Valid' if is_valid else 'Invalid'}")
        if is_valid != should_be_valid:
            all_passed = False
    
    return all_passed

def test_api_with_different_recipient():
    """Test API endpoint with different recipient"""
    print("\n🌐 TESTING API WITH DIFFERENT RECIPIENT")
    print("=" * 50)
    
    try:
        import requests
        
        recipient_email = input("📧 Enter recipient email for API test: ").strip()
        if not recipient_email:
            print("⏸️ Skipping API test - no recipient provided")
            return True
        
        test_request = {
            "email": recipient_email,
            "prediction": {
                "prediction": 30000.0,
                "confidence": 0.90
            },
            "patient_data": {
                "age": 35,
                "bmi": 24.0,
                "gender": "Female",
                "smoker": "No",
                "region": "South",
                "premium_annual_inr": 25000
            }
        }
        
        api_url = "http://localhost:8001/send-prediction-email"
        
        print(f"📡 Sending API request to: {api_url}")
        print(f"📧 Recipient: {recipient_email}")
        
        response = requests.post(
            api_url,
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response: {result}")
            
            if result.get("success"):
                print(f"🎉 Email sent via API to {recipient_email}")
                return True
            else:
                print(f"❌ API returned error: {result.get('message')}")
                return False
        else:
            print(f"❌ API call failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main testing function"""
    print("🧪 MULTIPLE RECIPIENT EMAIL TESTING")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 60)
    
    # Test 1: Email Validation
    validation_ok = test_email_validation()
    
    # Test 2: Direct Email Service Test
    email_service_ok = test_multiple_recipients()
    
    # Test 3: API Test (optional)
    print("\n" + "=" * 50)
    api_test = input("🌐 Test API endpoint with different recipient? (y/n): ").lower().startswith('y')
    api_ok = True
    if api_test:
        api_ok = test_api_with_different_recipient()
    
    # Summary
    print("\n📋 TESTING SUMMARY")
    print("=" * 50)
    print(f"Email Validation: {'✅ PASSED' if validation_ok else '❌ FAILED'}")
    print(f"Email Service: {'✅ PASSED' if email_service_ok else '❌ FAILED'}")
    print(f"API Test: {'✅ PASSED' if api_ok else '❌ FAILED' if api_test else '⏸️ SKIPPED'}")
    
    if validation_ok and email_service_ok:
        print("\n🎉 MULTIPLE RECIPIENT EMAIL FUNCTIONALITY WORKING!")
        print("\n📝 How to use:")
        print("1. Enter any valid email address in the prediction form")
        print("2. Generate a prediction")
        print("3. Click 'Email Report' button")
        print("4. Email will be sent to the specified address")
        print("5. Check the recipient's inbox/spam folder")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")

if __name__ == "__main__":
    main()
