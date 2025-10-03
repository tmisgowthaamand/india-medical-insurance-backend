#!/usr/bin/env python3
"""
Render Environment Setup for MediCare+ Email Fix
Shows the exact environment variables needed for Render deployment
"""

def show_render_environment_setup():
    """Display the environment variables needed for Render"""
    print("🚀 RENDER ENVIRONMENT SETUP - MediCare+ Email Fix")
    print("="*70)
    print()
    print("📋 REQUIRED ENVIRONMENT VARIABLES FOR RENDER:")
    print("-" * 50)
    print()
    print("Variable Name: GMAIL_EMAIL")
    print("Value: gokrishna98@gmail.com")
    print()
    print("Variable Name: GMAIL_APP_PASSWORD") 
    print("Value: lwkvzupqanxvafrm")
    print()
    print("="*70)
    print("🔧 HOW TO SET THESE IN RENDER:")
    print("="*70)
    print()
    print("1. Go to https://dashboard.render.com")
    print("2. Select your MediCare+ backend service")
    print("3. Click on 'Environment' tab")
    print("4. Click 'Add Environment Variable'")
    print("5. Add GMAIL_EMAIL with value: gokrishna98@gmail.com")
    print("6. Add GMAIL_APP_PASSWORD with value: lwkvzupqanxvafrm")
    print("7. Click 'Save Changes'")
    print("8. Your service will automatically redeploy")
    print()
    print("="*70)
    print("✅ VERIFICATION:")
    print("="*70)
    print()
    print("After setting the environment variables:")
    print("1. Wait for the service to redeploy (2-3 minutes)")
    print("2. Test the email functionality from your frontend")
    print("3. Check the service logs for 'EMAIL SERVICE: ✅ ENABLED'")
    print("4. Try sending a prediction report via email")
    print()
    print("🎉 Email functionality should now work correctly!")
    print("📧 Users will receive prediction reports in their Gmail inbox")

if __name__ == "__main__":
    show_render_environment_setup()
