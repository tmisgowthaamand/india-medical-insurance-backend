#!/usr/bin/env python3
"""
Simple SendGrid Test - MediCare+ Platform
Quick test to verify SendGrid is working
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_sendgrid_simple():
    """Simple test of SendGrid functionality"""
    print("🧪 SIMPLE SENDGRID TEST")
    print("="*60)
    
    # Check if SendGrid API key is set
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    
    if not sendgrid_key:
        print("❌ SENDGRID_API_KEY not found in environment")
        print("🔧 Please set it in Render dashboard:")
        print("   1. Go to Render dashboard")
        print("   2. Select your service")
        print("   3. Environment tab")
        print("   4. Add: SENDGRID_API_KEY=your_api_key")
        return
    
    print(f"✅ SendGrid API Key found: {sendgrid_key[:10]}...")
    
    # Test the email service
    try:
        # Try to import the email service
        try:
            from render_http_email_service import render_http_email_service
            email_service = render_http_email_service
            service_name = "HTTP Email Service"
        except ImportError:
            from render_builtin_email_service import render_builtin_email_service
            email_service = render_builtin_email_service
            service_name = "Builtin Email Service"
        
        print(f"📧 Using: {service_name}")
        
        # Check available providers
        providers = email_service.available_providers
        provider_names = [p['name'] for p in providers]
        print(f"📋 Available providers: {provider_names}")
        
        if 'SendGrid' not in provider_names:
            print("❌ SendGrid not in available providers")
            print("🔧 Check if SENDGRID_API_KEY is set correctly")
            return
        
        print("✅ SendGrid is available")
        
        # Send test email
        test_email = "gowthaamaneswar1998@gmail.com"
        test_prediction = {
            "prediction": 15873.78,
            "confidence": 0.85
        }
        test_patient_data = {
            "age": 25,
            "bmi": 23.5,
            "gender": "Male",
            "smoker": "No",
            "region": "South",
            "premium_annual_inr": 15000
        }
        
        print(f"\n📤 Sending test email to: {test_email}")
        print("⏳ Please wait...")
        
        result = await email_service.send_prediction_email(
            recipient_email=test_email,
            prediction_data=test_prediction,
            patient_data=test_patient_data,
            user_id="sendgrid_test"
        )
        
        print(f"\n📊 RESULT:")
        print(f"Success: {'✅ YES' if result['success'] else '❌ NO'}")
        print(f"Message: {result['message']}")
        print(f"Provider: {result.get('provider', 'Unknown')}")
        print(f"Time: {result.get('processing_time', 0):.2f}s")
        
        if result['success'] and 'SendGrid' in result.get('provider', ''):
            print("\n🎉 SUCCESS! Email sent via SendGrid")
            print("📧 Check Gmail inbox for MediCare+ report")
            print("💡 If not in inbox, check spam folder")
        elif result['success'] and 'Local Storage' in result.get('provider', ''):
            print("\n⚠️ Email stored locally (SendGrid not working)")
            print("🔧 Check SendGrid API key configuration")
        else:
            print("\n❌ Email sending failed")
            print("🔧 Check SendGrid setup and API key")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

def show_sendgrid_status():
    """Show current SendGrid configuration status"""
    print("\n" + "="*60)
    print("📊 SENDGRID CONFIGURATION STATUS")
    print("="*60)
    
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    
    if sendgrid_key:
        print("✅ SendGrid API Key: CONFIGURED")
        print(f"   Key starts with: {sendgrid_key[:10]}...")
        print(f"   Key length: {len(sendgrid_key)} characters")
        
        if sendgrid_key.startswith("SG."):
            print("✅ Key format: VALID (starts with SG.)")
        else:
            print("❌ Key format: INVALID (should start with SG.)")
            
    else:
        print("❌ SendGrid API Key: NOT CONFIGURED")
        print("\n🔧 TO FIX THIS:")
        print("1. Get SendGrid API key from https://sendgrid.com")
        print("2. In Render dashboard, add environment variable:")
        print("   SENDGRID_API_KEY=your_api_key_here")
        print("3. Redeploy your service")

if __name__ == "__main__":
    show_sendgrid_status()
    print()
    asyncio.run(test_sendgrid_simple())
