#!/usr/bin/env python3
"""
Gmail Setup Helper for MediCare+ Platform
Helps configure Gmail App Password for sending emails
"""

import os
import webbrowser
from dotenv import load_dotenv

def setup_gmail_app_password():
    """Guide user through Gmail App Password setup"""
    print("🏥 MediCare+ Gmail Setup Helper")
    print("="*50)
    
    email = "gokrishna98@gmail.com"
    print(f"📧 Setting up Gmail for: {email}")
    
    print("\n📋 Steps to generate Gmail App Password:")
    print("1. Enable 2-Factor Authentication (if not already enabled)")
    print("2. Generate App Password for MediCare+ Platform")
    print("3. Update .env file with the app password")
    
    print(f"\n🔗 Opening Gmail App Password page for {email}...")
    
    # Open Gmail App Password page
    app_password_url = "https://myaccount.google.com/apppasswords"
    try:
        webbrowser.open(app_password_url)
        print(f"✅ Opened: {app_password_url}")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"📋 Please manually visit: {app_password_url}")
    
    print("\n📝 Instructions:")
    print("1. Sign in with gokrishna98@gmail.com")
    print("2. Select 'Mail' from the dropdown")
    print("3. Select 'Other (Custom name)' and enter: 'MediCare+ Platform'")
    print("4. Click 'Generate'")
    print("5. Copy the 16-character app password")
    
    print("\n⏳ Waiting for you to generate the app password...")
    app_password = input("📋 Paste the generated app password here: ").strip()
    
    if len(app_password) == 16 or len(app_password) == 19:  # With or without spaces
        # Remove spaces if present
        app_password = app_password.replace(" ", "")
        
        # Update .env file
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Replace the placeholder
            updated_content = content.replace(
                "GMAIL_APP_PASSWORD=your-gmail-app-password-here",
                f"GMAIL_APP_PASSWORD={app_password}"
            )
            
            with open(env_file, 'w') as f:
                f.write(updated_content)
            
            print("✅ .env file updated successfully!")
            print("🔄 Please restart the backend server to apply changes")
            print("📧 Email functionality is now ready!")
            
        else:
            print("❌ .env file not found")
            print(f"📋 Please manually add: GMAIL_APP_PASSWORD={app_password}")
    
    else:
        print("❌ Invalid app password format. Should be 16 characters.")
        print("💡 Please try again with the correct app password")

def test_email_config():
    """Test current email configuration"""
    load_dotenv()
    
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print("\n🧪 Testing Email Configuration:")
    print(f"📧 Gmail Email: {gmail_email}")
    print(f"🔑 App Password: {'✅ Configured' if gmail_password and gmail_password != 'your-gmail-app-password-here' else '❌ Not configured'}")
    
    if gmail_email == "gokrishna98@gmail.com" and gmail_password and gmail_password != "your-gmail-app-password-here":
        print("✅ Email configuration looks good!")
        print("📧 Ready to send emails to Gmail inbox")
    else:
        print("⚠️ Email configuration needs setup")

if __name__ == "__main__":
    print("🏥 MediCare+ Gmail Configuration")
    print("="*40)
    
    choice = input("Choose option:\n1. Setup Gmail App Password\n2. Test current configuration\nEnter (1 or 2): ").strip()
    
    if choice == "1":
        setup_gmail_app_password()
    elif choice == "2":
        test_email_config()
    else:
        print("❌ Invalid choice. Please run again and choose 1 or 2.")
