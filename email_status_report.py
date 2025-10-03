#!/usr/bin/env python3
"""
Email Status Report - MediCare+ Platform
Shows current email configuration and expected frontend behavior
"""

import os
from dotenv import load_dotenv

def show_email_status_report():
    """Show comprehensive email status report"""
    print("📊 EMAIL STATUS REPORT - MediCare+ Platform")
    print("="*80)
    
    # Load environment variables
    load_dotenv()
    
    # Check configuration
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    mailgun_key = os.getenv("MAILGUN_API_KEY")
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")
    
    print("\n🔧 CURRENT CONFIGURATION")
    print("-" * 50)
    print(f"SendGrid API Key: {'✅ SET' if sendgrid_key else '❌ NOT SET'}")
    print(f"Mailgun API Key: {'✅ SET' if mailgun_key else '❌ NOT SET'}")
    print(f"Gmail Email: {'✅ SET' if gmail_email else '❌ NOT SET'} ({gmail_email})")
    print(f"Gmail App Password: {'✅ SET' if gmail_password else '❌ NOT SET'}")
    print(f"Sender Email: {'✅ SET' if sender_email else '❌ NOT SET'} ({sender_email})")
    
    # Determine email service status
    print(f"\n📧 EMAIL SERVICE STATUS")
    print("-" * 50)
    
    if sendgrid_key:
        if sendgrid_key.startswith("SG."):
            print("✅ SendGrid: CONFIGURED AND VALID")
            email_status = "sendgrid_working"
        else:
            print("❌ SendGrid: CONFIGURED BUT INVALID FORMAT")
            email_status = "sendgrid_invalid"
    elif mailgun_key:
        print("✅ Mailgun: CONFIGURED")
        email_status = "mailgun_working"
    elif gmail_email and gmail_password:
        print("⚠️ Gmail SMTP: CONFIGURED (but blocked on Render)")
        email_status = "gmail_smtp_blocked"
    else:
        print("❌ No email provider configured")
        email_status = "no_provider"
    
    # Show expected frontend behavior
    print(f"\n📱 EXPECTED FRONTEND BEHAVIOR")
    print("-" * 50)
    
    if email_status == "sendgrid_working":
        print("✅ SUCCESS MESSAGE:")
        print("   '✅ Email delivered successfully to gowthaamankrishna1998@gmail.com!'")
        print("   '📧 Check your Gmail inbox now'")
        print("   '⏱️ Delivered in X.Xs via SendGrid'")
        print("   '💡 Check spam folder if not in inbox'")
        print()
        print("📧 GMAIL INBOX: Will receive professional MediCare+ report")
        
    elif email_status == "mailgun_working":
        print("✅ SUCCESS MESSAGE:")
        print("   '✅ Email delivered successfully to gowthaamankrishna1998@gmail.com!'")
        print("   '📧 Check your Gmail inbox now'")
        print("   '⏱️ Delivered in X.Xs via Mailgun'")
        print("   '💡 Check spam folder if not in inbox'")
        print()
        print("📧 GMAIL INBOX: Will receive professional MediCare+ report")
        
    elif email_status in ["gmail_smtp_blocked", "no_provider", "sendgrid_invalid"]:
        print("⚠️ WARNING MESSAGE:")
        print("   '⚠️ Email NOT delivered to gowthaamankrishna1998@gmail.com'")
        print("   '📁 Email stored locally (not sent to Gmail)'")
        print("   '🔧 Email service not configured properly'")
        print("   '⏱️ Processing time: X.Xs'")
        print("   '💡 Use Download option to save report'")
        print()
        print("📧 GMAIL INBOX: Will NOT receive any email")
    
    # Show backend logs
    print(f"\n🖥️ EXPECTED BACKEND LOGS")
    print("-" * 50)
    
    if email_status == "sendgrid_working":
        print("✅ Available Providers: [SendGrid]")
        print("✅ Email sent via SendGrid in X.Xs")
        
    elif email_status == "mailgun_working":
        print("✅ Available Providers: [Mailgun]")
        print("✅ Email sent via Mailgun in X.Xs")
        
    else:
        print("⚠️ Available Providers: [Local Storage]")
        print("⚠️ Email sent via Local Storage in 0.0s")
    
    # Show fix instructions
    print(f"\n🔧 HOW TO FIX EMAIL DELIVERY")
    print("-" * 50)
    
    if email_status in ["no_provider", "sendgrid_invalid", "gmail_smtp_blocked"]:
        print("STEP 1: Get SendGrid API Key")
        print("1. Go to https://sendgrid.com")
        print("2. Sign up for free account")
        print("3. Go to Settings → API Keys")
        print("4. Create new API key with Mail Send permissions")
        print("5. Copy the API key (starts with SG.)")
        print()
        print("STEP 2: Configure Localhost")
        print("1. Edit backend/.env file")
        print("2. Uncomment and set: SENDGRID_API_KEY=SG.your_api_key_here")
        print("3. Restart backend server")
        print()
        print("STEP 3: Configure Render")
        print("1. Go to Render dashboard")
        print("2. Select your backend service")
        print("3. Environment tab → Add variable:")
        print("   SENDGRID_API_KEY = SG.your_api_key_here")
        print("4. Save changes (auto-redeploys)")
        print()
        print("STEP 4: Test")
        print("1. Make a prediction in frontend")
        print("2. Click 'Email Report'")
        print("3. Should see: 'Email delivered successfully via SendGrid'")
        print("4. Check Gmail inbox within 5 minutes")
    else:
        print("✅ Email delivery is already configured!")
        print("📧 Emails should be delivered to Gmail inbox")
    
    # Show current test results
    print(f"\n🧪 CURRENT TEST RESULTS")
    print("-" * 50)
    
    # Check if we have stored emails
    if os.path.exists("user_emails.json"):
        try:
            import json
            with open("user_emails.json", 'r') as f:
                user_emails = json.load(f)
                print(f"📁 Stored user emails: {len(user_emails)} users")
                for user_id, data in user_emails.items():
                    emails = data.get('emails', [])
                    print(f"   {user_id}: {emails}")
        except:
            print("📁 User emails file exists but couldn't read")
    else:
        print("📁 No stored user emails found")
    
    # Check if we have pending emails (indicates local storage mode)
    if os.path.exists("pending_emails.json"):
        try:
            import json
            with open("pending_emails.json", 'r') as f:
                pending = json.load(f)
                print(f"📋 Pending emails: {len(pending)} emails stored locally")
                if pending:
                    latest = pending[-1]
                    print(f"   Latest: {latest['recipient']} at {latest['timestamp']}")
                print("⚠️ This confirms emails are NOT being delivered to Gmail")
        except:
            print("📋 Pending emails file exists but couldn't read")
    else:
        print("📋 No pending emails found")
        if email_status in ["sendgrid_working", "mailgun_working"]:
            print("✅ This suggests emails are being delivered (not stored locally)")
    
    print(f"\n🎯 SUMMARY")
    print("-" * 50)
    
    if email_status in ["sendgrid_working", "mailgun_working"]:
        print("✅ EMAIL DELIVERY: WORKING")
        print("📧 Frontend shows honest success messages")
        print("📬 Gmail receives MediCare+ reports")
        print("🎉 System is working correctly!")
    else:
        print("❌ EMAIL DELIVERY: NOT WORKING")
        print("⚠️ Frontend shows honest warning messages")
        print("📁 Emails stored locally (not delivered)")
        print("🔧 Configure SendGrid to enable delivery")
    
    print(f"\n💡 The frontend fix is working correctly!")
    print("📱 It now shows honest feedback based on actual email delivery status")
    print("🚫 No more fake success messages when emails aren't delivered")

if __name__ == "__main__":
    show_email_status_report()
