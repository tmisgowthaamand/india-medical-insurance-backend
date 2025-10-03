#!/usr/bin/env python3
"""
Test Gmail Credentials and Email Functionality
Verifies that Gmail credentials are properly configured and emails can be sent
"""

import os
import asyncio
from dotenv import load_dotenv
from fix_email_delivery_issue import FixedEmailService

# Load environment variables from .env file
load_dotenv()

async def main():
    print("🧪 TESTING GMAIL CREDENTIALS AND EMAIL FUNCTIONALITY")
    print("="*70)
    
    # Check environment variables
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print("📋 ENVIRONMENT VARIABLES CHECK:")
    print(f"   GMAIL_EMAIL: {gmail_email if gmail_email else '❌ NOT SET'}")
    print(f"   GMAIL_APP_PASSWORD: {'✅ SET' if gmail_password else '❌ NOT SET'}")
    print()
    
    if not gmail_email or not gmail_password:
        print("❌ GMAIL CREDENTIALS NOT CONFIGURED")
        print()
        print("🔧 TO FIX THIS ISSUE:")
        print("1. Go to your Render dashboard")
        print("2. Navigate to your backend service")
        print("3. Go to Environment tab")
        print("4. Add these environment variables:")
        print("   - GMAIL_EMAIL: your-gmail-address@gmail.com")
        print("   - GMAIL_APP_PASSWORD: your-16-character-app-password")
        print()
        print("📱 TO GET GMAIL APP PASSWORD:")
        print("1. Go to https://myaccount.google.com/security")
        print("2. Enable 2-Factor Authentication if not already enabled")
        print("3. Go to 'App passwords' section")
        print("4. Generate a new app password for 'Mail'")
        print("5. Use the 16-character password (without spaces)")
        print()
        return
    
    # Test the fixed email service
    service = FixedEmailService()
    
    # Test Gmail connection
    print("🔗 TESTING GMAIL CONNECTION...")
    connection_result = service.test_gmail_connection()
    
    if connection_result["success"]:
        print("✅ Gmail connection successful!")
        print(f"   SMTP Server: {connection_result.get('smtp_server')}")
        print(f"   Sender Email: {connection_result.get('sender_email')}")
    else:
        print("❌ Gmail connection failed!")
        print(f"   Error: {connection_result['error']}")
        print(f"   Details: {connection_result.get('details', 'N/A')}")
        
        if 'fix_instructions' in connection_result:
            print("\n🔧 FIX INSTRUCTIONS:")
            for instruction in connection_result['fix_instructions']:
                print(f"   {instruction}")
        return
    
    print()
    
    # Test sending email to the user's email address
    test_email = "perivihari8@gmail.com"  # The email from the user's request
    print(f"📧 TESTING EMAIL SEND TO: {test_email}")
    
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
    
    print("📤 Sending test email...")
    result = await service.send_prediction_email_with_honest_feedback(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data
    )
    
    print()
    print("📊 EMAIL SEND RESULT:")
    print(f"   Success: {'✅ YES' if result['success'] else '❌ NO'}")
    print(f"   Message: {result['message']}")
    
    if not result['success']:
        print(f"   Error Type: {result.get('error_type', 'unknown')}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
        if 'fix_instructions' in result:
            print("\n🔧 FIX INSTRUCTIONS:")
            for instruction in result['fix_instructions']:
                print(f"     {instruction}")
    else:
        print(f"   Processing Time: {result.get('processing_time', 'unknown')}s")
        print(f"   Delivery Status: {result.get('delivery_status', 'unknown')}")
    
    print()
    print("="*70)
    
    if result['success']:
        print("🎉 EMAIL FUNCTIONALITY IS WORKING!")
        print(f"✅ Check {test_email} inbox (including spam folder)")
    else:
        print("❌ EMAIL FUNCTIONALITY NEEDS FIXING")
        print("💡 Follow the fix instructions above")

if __name__ == "__main__":
    asyncio.run(main())
