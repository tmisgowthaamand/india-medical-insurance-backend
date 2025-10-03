#!/usr/bin/env python3
"""
Email Delivery Verification - MediCare+ Platform
Comprehensive testing and verification of email delivery
"""

import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def verify_email_delivery():
    """Comprehensive email delivery verification"""
    print("🔍 EMAIL DELIVERY VERIFICATION - MediCare+ Platform")
    print("="*80)
    
    # Step 1: Check email service configuration
    print("\n📋 STEP 1: Email Service Configuration")
    print("-" * 50)
    
    # Check environment variables
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    mailgun_key = os.getenv("MAILGUN_API_KEY")
    mailgun_domain = os.getenv("MAILGUN_DOMAIN")
    
    print(f"SendGrid API Key: {'✅ SET' if sendgrid_key else '❌ NOT SET'}")
    if sendgrid_key:
        print(f"   Key: {sendgrid_key[:15]}...")
        print(f"   Valid format: {'✅ YES' if sendgrid_key.startswith('SG.') else '❌ NO'}")
    
    print(f"Mailgun API Key: {'✅ SET' if mailgun_key else '❌ NOT SET'}")
    if mailgun_key:
        print(f"   Key: {mailgun_key[:15]}...")
        print(f"   Domain: {mailgun_domain}")
    
    # Step 2: Test email service initialization
    print("\n🔧 STEP 2: Email Service Initialization")
    print("-" * 50)
    
    try:
        # Try to import and initialize email service
        try:
            from render_http_email_service import render_http_email_service
            email_service = render_http_email_service
            service_type = "HTTP Email Service (with requests)"
        except ImportError:
            from render_builtin_email_service import render_builtin_email_service
            email_service = render_builtin_email_service
            service_type = "Builtin Email Service (urllib)"
        
        print(f"✅ Email service loaded: {service_type}")
        
        # Check available providers
        providers = email_service.available_providers
        provider_names = [p['name'] for p in providers]
        print(f"📋 Available providers: {provider_names}")
        
        if not providers:
            print("❌ No email providers available")
            return False
        
        # Check if we have actual email providers (not just storage)
        real_providers = [p for p in providers if p['type'] != 'storage']
        if not real_providers:
            print("⚠️ Only local storage available - emails won't be delivered")
            print("🔧 Configure SendGrid or Mailgun to enable email delivery")
        else:
            print(f"✅ Real email providers available: {[p['name'] for p in real_providers]}")
        
    except Exception as e:
        print(f"❌ Failed to initialize email service: {e}")
        return False
    
    # Step 3: Send test email with detailed tracking
    print("\n📧 STEP 3: Send Test Email")
    print("-" * 50)
    
    test_email = "gowthaamaneswar1998@gmail.com"
    test_prediction = {
        "prediction": 17823.90,
        "confidence": 0.92
    }
    test_patient_data = {
        "age": 26,
        "bmi": 24.2,
        "gender": "Male",
        "smoker": "No",
        "region": "South",
        "premium_annual_inr": 18000
    }
    
    print(f"📤 Sending test email to: {test_email}")
    print(f"💰 Prediction amount: ₹{test_prediction['prediction']:,.2f}")
    print("⏳ Sending email...")
    
    try:
        result = await email_service.send_prediction_email(
            recipient_email=test_email,
            prediction_data=test_prediction,
            patient_data=test_patient_data,
            user_id="verification_test"
        )
        
        print(f"\n📊 EMAIL RESULT:")
        print(f"Success: {'✅ YES' if result['success'] else '❌ NO'}")
        print(f"Message: {result['message']}")
        print(f"Provider: {result.get('provider', 'Unknown')}")
        print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
        
        # Analyze the result
        if result['success']:
            if 'SendGrid' in result.get('provider', ''):
                print("\n🎉 SUCCESS: Email sent via SendGrid")
                print("📧 Check Gmail inbox for MediCare+ report")
                print("⏰ Email should arrive within 1-5 minutes")
                return True
            elif 'Mailgun' in result.get('provider', ''):
                print("\n🎉 SUCCESS: Email sent via Mailgun")
                print("📧 Check Gmail inbox for MediCare+ report")
                print("⏰ Email should arrive within 1-5 minutes")
                return True
            elif 'Local Storage' in result.get('provider', ''):
                print("\n⚠️ WARNING: Email stored locally (not sent)")
                print("🔧 No email provider configured - emails won't reach Gmail")
                return False
            else:
                print(f"\n✅ Email sent via {result.get('provider', 'Unknown')}")
                return True
        else:
            print(f"\n❌ EMAIL FAILED: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Email test failed with exception: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Step 4: Check stored emails
    print("\n📁 STEP 4: Check Stored Emails")
    print("-" * 50)
    
    try:
        # Check user emails storage
        user_emails = email_service.get_user_emails("verification_test")
        print(f"Stored user emails: {user_emails}")
        
        # Check pending emails (if any)
        pending_file = "pending_emails.json"
        if os.path.exists(pending_file):
            with open(pending_file, 'r') as f:
                pending_emails = json.load(f)
                print(f"Pending emails count: {len(pending_emails)}")
                if pending_emails:
                    latest = pending_emails[-1]
                    print(f"Latest pending email: {latest['recipient']} at {latest['timestamp']}")
        else:
            print("No pending emails file found")
            
    except Exception as e:
        print(f"⚠️ Could not check stored emails: {e}")

def show_gmail_inbox_instructions():
    """Show instructions for finding emails in Gmail"""
    print("\n" + "="*80)
    print("📧 HOW TO FIND MEDICARE+ EMAILS IN GMAIL")
    print("="*80)
    print()
    print("🔍 Search Methods:")
    print("1. Search for: 'MediCare+'")
    print("2. Search for: 'Insurance Report'")
    print("3. Search for: 'from:gokrishna98@gmail.com'")
    print("4. Search for: 'subject:MediCare+'")
    print()
    print("📂 Check These Folders:")
    print("1. ✅ Primary Inbox")
    print("2. 📢 Promotions tab")
    print("3. 🗑️ Spam/Junk folder")
    print("4. 📋 All Mail")
    print()
    print("⏰ Delivery Time:")
    print("- SendGrid: 1-5 minutes")
    print("- Mailgun: 1-10 minutes")
    print("- Local Storage: Not delivered (stored locally)")
    print()
    print("🎯 Email Subject Format:")
    print("'🏥 MediCare+ Insurance Report - ₹XX,XXX'")
    print()
    print("📨 Sender Information:")
    print("- From: MediCare+ Insurance Platform")
    print("- Email: gokrishna98@gmail.com (or provider email)")
    print()
    print("💡 If emails are missing:")
    print("1. Check spam folder first")
    print("2. Add sender to contacts")
    print("3. Check email filters/rules")
    print("4. Wait 10-15 minutes for delivery")

async def main():
    """Main verification function"""
    success = await verify_email_delivery()
    show_gmail_inbox_instructions()
    
    print("\n" + "="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)
    
    if success:
        print("✅ EMAIL DELIVERY: WORKING")
        print("📧 Emails should be delivered to Gmail inbox")
        print("🎉 Check Gmail for MediCare+ reports")
    else:
        print("❌ EMAIL DELIVERY: NOT WORKING")
        print("🔧 Configure SendGrid or Mailgun API keys")
        print("📋 Emails are being stored locally only")
    
    print("\n🔧 QUICK FIX:")
    print("1. Get SendGrid API key from https://sendgrid.com")
    print("2. In Render dashboard, set: SENDGRID_API_KEY=your_key")
    print("3. Redeploy service")
    print("4. Test email delivery")

if __name__ == "__main__":
    asyncio.run(main())
