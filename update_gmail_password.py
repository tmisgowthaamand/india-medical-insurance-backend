#!/usr/bin/env python3
"""
Quick Gmail App Password Update Script
Run this after generating your Gmail App Password
"""

import os

def update_gmail_password():
    """Update Gmail App Password in .env file"""
    print("🔧 Gmail App Password Update Tool")
    print("="*40)
    
    print("📧 Current email: gokrishna98@gmail.com")
    print("\n📋 Steps you should have completed:")
    print("1. ✅ Visited: https://myaccount.google.com/apppasswords")
    print("2. ✅ Signed in with gokrishna98@gmail.com")
    print("3. ✅ Generated app password for 'MediCare Platform'")
    print("4. ✅ Copied the 16-character app password")
    
    print("\n🔑 Now paste your Gmail App Password:")
    app_password = input("App Password (16 characters): ").strip()
    
    # Remove spaces if present
    app_password = app_password.replace(" ", "")
    
    if len(app_password) != 16:
        print(f"❌ Invalid length. Expected 16 characters, got {len(app_password)}")
        print("💡 App password should look like: abcdabcdabcdabcd")
        return False
    
    # Update .env file
    env_file = ".env"
    if not os.path.exists(env_file):
        print("❌ .env file not found!")
        return False
    
    try:
        # Read current content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace the placeholder
        old_line = "GMAIL_APP_PASSWORD=your-gmail-app-password-here"
        new_line = f"GMAIL_APP_PASSWORD={app_password}"
        
        if old_line in content:
            updated_content = content.replace(old_line, new_line)
            
            # Write back to file
            with open(env_file, 'w') as f:
                f.write(updated_content)
            
            print("✅ Gmail App Password updated successfully!")
            print("🔄 Please restart the backend server:")
            print("   1. Stop current server (Ctrl+C)")
            print("   2. Run: uvicorn app:app --host 0.0.0.0 --port 8001 --reload")
            print("📧 Email functionality will then be ready!")
            return True
        else:
            print("⚠️ Could not find placeholder in .env file")
            print(f"💡 Please manually replace 'your-gmail-app-password-here' with: {app_password}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

if __name__ == "__main__":
    success = update_gmail_password()
    if success:
        print("\n🎉 Setup complete! Your emails will now be sent to Gmail inbox.")
    else:
        print("\n❌ Setup failed. Please try again or update manually.")
