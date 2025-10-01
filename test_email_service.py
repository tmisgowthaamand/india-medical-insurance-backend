#!/usr/bin/env python3
"""
Test Email Service for MediCare+ Platform
Tests the email functionality to ensure it works properly
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from email_service import email_service

def test_email_configuration():
    """Test email service configuration"""
    print("🔧 Testing Email Service Configuration")
    print("=" * 50)
    
    # Check environment variables
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"Gmail Email: {gmail_email}")
    print(f"Gmail App Password: {'*' * len(gmail_password) if gmail_password else 'Not set'}")
    print(f"Email Service Enabled: {email_service.is_email_enabled()}")
    
    if not email_service.is_email_enabled():
        print("❌ Email service is not properly configured")
        return False
    
    print("✅ Email service configuration looks good")
    return True

def test_email_sending():
    """Test actual email sending"""
    print("\n📧 Testing Email Sending")
    print("=" * 50)
    
    # Test data
    test_prediction = {
        "prediction": 25000.0,
        "confidence": 0.85
    }
    
    test_patient_data = {
        "age": 35,
        "bmi": 23.0,
        "gender": "Male",
        "smoker": "No",
        "region": "East",
        "premium_annual_inr": 30000
    }
    
    test_email = "gokrishna98@gmail.com"  # Using the configured email
    
    print(f"Sending test email to: {test_email}")
    print("Test prediction data:", test_prediction)
    print("Test patient data:", test_patient_data)
    
    try:
        success = email_service.send_prediction_email(
            recipient_email=test_email,
            prediction_data=test_prediction,
            patient_data=test_patient_data
        )
        
        if success:
            print("✅ Email sent successfully!")
            print("📬 Check your inbox and spam folder")
            return True
        else:
            print("❌ Email sending failed")
            return False
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False

def main():
    """Main test function"""
    print("🏥 MediCare+ Email Service Test")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_email_configuration()
    
    if not config_ok:
        print("\n❌ Email configuration test failed")
        print("💡 Please check your .env file and ensure GMAIL_EMAIL and GMAIL_APP_PASSWORD are set")
        return
    
    # Test email sending
    email_ok = test_email_sending()
    
    if email_ok:
        print("\n🎉 All email tests passed!")
        print("📧 Email service is working properly")
    else:
        print("\n❌ Email sending test failed")
        print("💡 Check Gmail settings and app password")

if __name__ == "__main__":
    main()
