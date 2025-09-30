#!/usr/bin/env python3
"""
Fix Email Endpoint Issues
Ensures proper email sending and response handling
"""

import os
import sys
import json
from datetime import datetime

def fix_email_endpoint():
    """Fix the email endpoint in app.py"""
    
    app_file = "app.py"
    
    if not os.path.exists(app_file):
        print("❌ app.py not found!")
        return False
    
    # Read the current app.py
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the email endpoint
    email_endpoint_start = content.find('@app.post("/send-prediction-email"')
    if email_endpoint_start == -1:
        print("❌ Email endpoint not found!")
        return False
    
    # Find the end of the email endpoint function
    email_endpoint_end = content.find('@app.post("/test-email")', email_endpoint_start)
    if email_endpoint_end == -1:
        email_endpoint_end = len(content)
    
    # Extract the current endpoint
    current_endpoint = content[email_endpoint_start:email_endpoint_end]
    
    # Create the improved email endpoint
    improved_endpoint = '''@app.post("/send-prediction-email", response_model=EmailResponse)
async def send_prediction_email(request: EmailPredictionRequest):
    """
    Send prediction report via email with improved error handling
    """
    try:
        print(f"📧 Processing email request for: {request.email}")
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, str(request.email)):
            return EmailResponse(
                success=False,
                message=f"Invalid email format: {request.email}"
            )
        
        # Save email to users table if it doesn't exist
        try:
            if supabase_client.is_enabled():
                email_result = await supabase_client.save_email_to_users(str(request.email))
                if email_result.get("success"):
                    print(f"✅ Email {request.email} saved to users table")
                else:
                    print(f"⚠️ Failed to save email to users table: {email_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️ Error saving email to users table: {e}")
        
        # Check Gmail configuration
        gmail_email = os.getenv("GMAIL_EMAIL")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not gmail_email or not gmail_password:
            print("⚠️ Gmail credentials not configured")
            return EmailResponse(
                success=False,
                message="Email service not configured. Please contact administrator."
            )
        
        # Send email using the email service
        print(f"📧 Attempting to send email to {request.email}...")
        success = email_service.send_prediction_email(
            recipient_email=str(request.email),
            prediction_data=request.prediction,
            patient_data=request.patient_data
        )
        
        if success:
            print(f"✅ Email sent successfully to {request.email}")
            return EmailResponse(
                success=True,
                message=f"Prediction report sent successfully to {request.email}! Check your inbox."
            )
        else:
            print(f"❌ Failed to send email to {request.email}")
            return EmailResponse(
                success=False,
                message=f"Failed to send email to {request.email}. Please try again or contact support."
            )
            
    except Exception as e:
        print(f"❌ Email processing error: {e}")
        return EmailResponse(
            success=False,
            message=f"Email processing failed: {str(e)}"
        )

'''
    
    # Replace the endpoint
    new_content = content[:email_endpoint_start] + improved_endpoint + content[email_endpoint_end:]
    
    # Write the updated content
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Email endpoint updated successfully!")
    return True

def test_email_endpoint_fix():
    """Test that the email endpoint fix was applied correctly"""
    
    app_file = "app.py"
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key improvements
    checks = [
        ('Email validation', 'email_pattern = r\'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{2,}$\''),
        ('Gmail config check', 'gmail_email = os.getenv("GMAIL_EMAIL")'),
        ('Success response', 'Prediction report sent successfully'),
        ('Error handling', 'Email processing failed'),
        ('Proper logging', 'print(f"📧 Attempting to send email')
    ]
    
    print("🧪 Testing email endpoint fix...")
    all_passed = True
    
    for check_name, check_pattern in checks:
        if check_pattern in content:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Missing")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🔧 FIXING EMAIL ENDPOINT")
    print("=" * 40)
    
    if fix_email_endpoint():
        print("\n🧪 TESTING FIX")
        print("=" * 40)
        
        if test_email_endpoint_fix():
            print("\n🎉 Email endpoint fix completed successfully!")
            print("\n📝 Next steps:")
            print("1. Restart the backend server")
            print("2. Test email functionality from frontend")
            print("3. Check backend console for detailed logs")
        else:
            print("\n❌ Some checks failed. Please review the fix.")
    else:
        print("\n❌ Failed to fix email endpoint.")
