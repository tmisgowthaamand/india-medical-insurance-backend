#!/usr/bin/env python3
"""
Test Script to Verify Email Functionality on Render
"""

import os
import asyncio
from bulletproof_email_service import bulletproof_email_service

async def test_email_functionality():
    """Test email functionality on Render"""
    print("🧪 Testing Email Functionality on Render")
    print("=" * 50)
    
    # Check environment variables
    print("🔍 Checking Environment Variables:")
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"GMAIL_EMAIL: {gmail_email if gmail_email else '❌ NOT SET'}")
    print(f"GMAIL_APP_PASSWORD: {'✅ SET' if gmail_password else '❌ NOT SET'}")
    
    if not gmail_email or not gmail_password:
        print("❌ Gmail credentials not found in environment variables")
        print("💡 Please set GMAIL_EMAIL and GMAIL_APP_PASSWORD in Render environment variables")
        return
    
    # Test connection
    print("\n🔗 Testing Gmail Connection:")
    connection_result = bulletproof_email_service.test_gmail_connection()
    
    if connection_result["success"]:
        print("✅ Gmail connection successful")
    else:
        print("❌ Gmail connection failed")
        print(f"Error: {connection_result.get('error', 'Unknown')}")
        print(f"Message: {connection_result.get('message', 'No message')}")
        if 'fix_instructions' in connection_result:
            print("🔧 Fix Instructions:")
            for instruction in connection_result['fix_instructions']:
                print(f"  {instruction}")
        return
    
    # Test email sending
    print("\n📧 Testing Email Sending:")
    test_email = "gowthaamankrishna1998@gmail.com"  # User's email
    test_prediction = {
        "prediction": 19777.48,
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
    
    result = await bulletproof_email_service.send_prediction_email(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data
    )
    
    if result["success"]:
        print("✅ Email sent successfully!")
        print(f"Message: {result['message']}")
        print(f"Processing Time: {result.get('processing_time', 0)}s")
    else:
        print("❌ Email sending failed")
        print(f"Message: {result['message']}")
        if 'fix_instructions' in result:
            print("🔧 Fix Instructions:")
            for instruction in result['fix_instructions']:
                print(f"  {instruction}")

if __name__ == "__main__":
    asyncio.run(test_email_functionality())