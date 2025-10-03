#!/usr/bin/env python3
"""
Bulletproof Email Service for MediCare+ Platform
Handles all Gmail connection issues on Render deployment with comprehensive error handling
"""

import os
import smtplib
import ssl
import asyncio
import time
import socket
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any
import re

class BulletproofEmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Read environment variables with multiple fallbacks
        self.sender_email = self._get_email_credential()
        self.sender_password = self._get_password_credential()
        self.sender_name = "MediCare+ Platform"
        
        # Check if credentials are available
        self.email_enabled = bool(self.sender_email and self.sender_password)
        
        # Aggressive timeout settings for Render
        self.connection_timeout = 30
        self.send_timeout = 45
        self.total_timeout = 90
        
        print("="*80)
        print("🛡️ BULLETPROOF EMAIL SERVICE - MediCare+ Platform")
        print("="*80)
        print(f"📧 Gmail Email: {self.sender_email if self.sender_email else '❌ NOT FOUND'}")
        print(f"🔑 App Password: {'✅ FOUND' if self.sender_password else '❌ NOT FOUND'}")
        print(f"🌐 Service Status: {'✅ READY' if self.email_enabled else '❌ DISABLED'}")
        print(f"🏗️ Platform: {'Render' if 'RENDER' in os.environ else 'Local'}")
        print("="*80)
        
        if not self.email_enabled:
            self._show_setup_instructions()
    
    def _get_email_credential(self):
        """Get email credential with multiple fallback methods"""
        # Try multiple environment variable names
        email_vars = ["GMAIL_EMAIL", "EMAIL_USER", "SMTP_EMAIL", "SENDER_EMAIL"]
        
        for var in email_vars:
            email = os.getenv(var)
            if email:
                print(f"✅ Found email in {var}: {email}")
                return email
        
        # Fallback to hardcoded for testing (remove in production)
        fallback_email = "gokrishna98@gmail.com"
        print(f"⚠️ Using fallback email: {fallback_email}")
        return fallback_email
    
    def _get_password_credential(self):
        """Get password credential with multiple fallback methods"""
        # Try multiple environment variable names
        password_vars = ["GMAIL_APP_PASSWORD", "EMAIL_PASSWORD", "SMTP_PASSWORD", "APP_PASSWORD"]
        
        for var in password_vars:
            password = os.getenv(var)
            if password:
                print(f"✅ Found password in {var}: {len(password)} chars")
                return password
        
        # Fallback to hardcoded for testing (remove in production)
        fallback_password = "lwkvzupqanxvafrm"
        print(f"⚠️ Using fallback password: {len(fallback_password)} chars")
        return fallback_password
    
    def _show_setup_instructions(self):
        """Show setup instructions for missing credentials"""
        print("🔧 EMAIL SERVICE SETUP REQUIRED")
        print("-" * 50)
        print("Missing Gmail credentials. Set ANY of these environment variables:")
        print()
        print("For Email:")
        print("  GMAIL_EMAIL=gokrishna98@gmail.com")
        print("  EMAIL_USER=gokrishna98@gmail.com")
        print("  SMTP_EMAIL=gokrishna98@gmail.com")
        print()
        print("For Password:")
        print("  GMAIL_APP_PASSWORD=lwkvzupqanxvafrm")
        print("  EMAIL_PASSWORD=lwkvzupqanxvafrm")
        print("  SMTP_PASSWORD=lwkvzupqanxvafrm")
        print()
        print("🚀 For Render deployment:")
        print("1. Go to Render Dashboard")
        print("2. Select your service")
        print("3. Environment tab")
        print("4. Add: GMAIL_EMAIL=gokrishna98@gmail.com")
        print("5. Add: GMAIL_APP_PASSWORD=lwkvzupqanxvafrm")
    
    def test_gmail_connection(self) -> Dict[str, Any]:
        """Bulletproof Gmail connection test with comprehensive diagnostics"""
        print("🔗 BULLETPROOF Gmail Connection Test")
        print("-" * 50)
        
        if not self.email_enabled:
            return {
                "success": False,
                "error": "Credentials missing",
                "message": "❌ Gmail credentials not found in environment variables"
            }
        
        # Test 1: Basic connectivity
        print("🌐 Testing internet connectivity...")
        try:
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=10)
            print("   ✅ Internet connection OK")
        except Exception as e:
            print(f"   ❌ Internet connection failed: {e}")
            return {
                "success": False,
                "error": "No internet",
                "message": "❌ No internet connection available"
            }
        
        # Test 2: DNS resolution
        print("🔍 Testing Gmail DNS resolution...")
        try:
            import socket
            socket.gethostbyname(self.smtp_server)
            print(f"   ✅ {self.smtp_server} resolved successfully")
        except Exception as e:
            print(f"   ❌ DNS resolution failed: {e}")
            return {
                "success": False,
                "error": "DNS failure",
                "message": f"❌ Cannot resolve {self.smtp_server}"
            }
        
        # Test 3: SMTP connection with multiple attempts
        for attempt in range(3):
            print(f"📡 SMTP Connection Attempt {attempt + 1}/3...")
            
            try:
                # Set aggressive socket timeout
                original_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(self.connection_timeout)
                
                try:
                    # Create SSL context with relaxed settings
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    print(f"   📡 Connecting to {self.smtp_server}:{self.smtp_port}...")
                    with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
                        print("   ✅ Connected to Gmail SMTP server")
                        
                        print("   🔐 Starting TLS...")
                        server.starttls(context=context)
                        print("   ✅ TLS established")
                        
                        print("   🔑 Authenticating...")
                        server.login(self.sender_email, self.sender_password)
                        print("   ✅ Authentication successful")
                        
                        return {
                            "success": True,
                            "message": "✅ Gmail connection successful",
                            "attempt": attempt + 1,
                            "smtp_server": f"{self.smtp_server}:{self.smtp_port}"
                        }
                        
                finally:
                    socket.setdefaulttimeout(original_timeout)
                    
            except smtplib.SMTPAuthenticationError as e:
                error_code = str(e).split()[0] if str(e) else "Unknown"
                print(f"   ❌ Authentication failed (attempt {attempt + 1}): {error_code}")
                
                if attempt == 2:  # Last attempt
                    return {
                        "success": False,
                        "error": "Authentication failed",
                        "message": "❌ Gmail authentication failed - check app password",
                        "details": str(e),
                        "fix_instructions": [
                            "1. Verify Gmail email is correct",
                            "2. Generate new Gmail App Password",
                            "3. Ensure 2FA is enabled on Gmail",
                            "4. Update GMAIL_APP_PASSWORD in Render"
                        ]
                    }
                    
            except smtplib.SMTPConnectError as e:
                print(f"   ❌ Connection failed (attempt {attempt + 1}): {e}")
                
                if attempt == 2:  # Last attempt
                    return {
                        "success": False,
                        "error": "Connection failed",
                        "message": "❌ Cannot connect to Gmail SMTP server",
                        "details": str(e)
                    }
                    
            except socket.timeout:
                print(f"   ❌ Timeout (attempt {attempt + 1}): {self.connection_timeout}s")
                
                if attempt == 2:  # Last attempt
                    return {
                        "success": False,
                        "error": "Timeout",
                        "message": f"❌ Connection timed out after {self.connection_timeout}s",
                        "details": "Gmail server not responding"
                    }
                    
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Unknown error (attempt {attempt + 1}): {error_msg}")
                
                if attempt == 2:  # Last attempt
                    return {
                        "success": False,
                        "error": "Unknown error",
                        "message": "❌ Gmail connection failed with unknown error",
                        "details": error_msg,
                        "python_version": sys.version,
                        "platform": os.name
                    }
            
            # Wait before retry
            if attempt < 2:
                wait_time = (attempt + 1) * 2
                print(f"   ⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        return {
            "success": False,
            "error": "All attempts failed",
            "message": "❌ All connection attempts failed"
        }
    
    async def send_prediction_email(self, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> Dict[str, Any]:
        """Bulletproof email sending with comprehensive error handling"""
        start_time = time.time()
        
        print(f"📧 BULLETPROOF EMAIL SEND: {recipient_email}")
        print("-" * 60)
        
        # Step 1: Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, recipient_email):
            return {
                "success": False,
                "message": f"❌ Invalid email format: {recipient_email}"
            }
        
        # Step 2: Check service availability
        if not self.email_enabled:
            return {
                "success": False,
                "message": "❌ Email service not configured. Please set Gmail credentials in environment variables."
            }
        
        # Step 3: Test connection first
        print("🔍 Pre-flight connection test...")
        connection_test = self.test_gmail_connection()
        if not connection_test["success"]:
            return {
                "success": False,
                "message": connection_test["message"],
                "error_type": connection_test["error"],
                "details": connection_test.get("details", ""),
                "fix_instructions": connection_test.get("fix_instructions", [])
            }
        
        print("✅ Connection test passed, proceeding with email...")
        
        # Step 4: Prepare email content
        try:
            email_content = self._prepare_email_content(prediction_data, patient_data, recipient_email)
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Failed to prepare email content: {str(e)}"
            }
        
        # Step 5: Send email with retries
        for attempt in range(3):
            try:
                print(f"📤 Email send attempt {attempt + 1}/3...")
                await self._send_email_with_retries(email_content, recipient_email)
                
                processing_time = round(time.time() - start_time, 2)
                success_message = f"✅ Email sent successfully to {recipient_email}! Check inbox (including spam folder)."
                
                print(f"🎉 EMAIL DELIVERED in {processing_time}s")
                
                return {
                    "success": True,
                    "message": success_message,
                    "processing_time": processing_time,
                    "delivery_status": "delivered",
                    "recipient": recipient_email,
                    "attempt": attempt + 1
                }
                
            except Exception as e:
                error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                print(f"   ❌ {error_msg}")
                
                if attempt == 2:  # Last attempt
                    processing_time = round(time.time() - start_time, 2)
                    return {
                        "success": False,
                        "message": f"❌ Email sending failed after 3 attempts: {str(e)}",
                        "processing_time": processing_time,
                        "last_error": str(e)
                    }
                
                # Wait before retry
                wait_time = (attempt + 1) * 2
                print(f"   ⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
        
        return {
            "success": False,
            "message": "❌ All email sending attempts failed"
        }
    
    async def _send_email_with_retries(self, email_content: Dict, recipient_email: str):
        """Send email with proper error handling"""
        loop = asyncio.get_event_loop()
        
        def send_sync():
            # Set socket timeout
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.send_timeout)
            
            try:
                # Create SSL context
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
                    # Enable debug for troubleshooting
                    # server.set_debuglevel(1)
                    
                    print("   🔐 Starting TLS...")
                    server.starttls(context=context)
                    
                    print("   🔑 Authenticating...")
                    server.login(self.sender_email, self.sender_password)
                    
                    print("   📧 Sending email...")
                    result = server.sendmail(
                        from_addr=self.sender_email,
                        to_addrs=[recipient_email],
                        msg=email_content["message"].as_string()
                    )
                    
                    # Check for rejected recipients
                    if result:
                        raise smtplib.SMTPRecipientsRefused(result)
                    
                    print("   ✅ Email sent successfully")
                    
            finally:
                socket.setdefaulttimeout(original_timeout)
        
        # Run with timeout
        await asyncio.wait_for(
            loop.run_in_executor(None, send_sync),
            timeout=self.total_timeout
        )
    
    def _prepare_email_content(self, prediction_data: Dict, patient_data: Dict, recipient_email: str) -> Dict:
        """Prepare professional email content"""
        prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
        confidence = round(prediction_data.get('confidence', 0) * 100, 1)
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏥 MediCare+ Insurance Report - {prediction_amount}"
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['To'] = recipient_email
        msg['Reply-To'] = self.sender_email
        
        # Professional HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MediCare+ Prediction Report</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px;">
                    <h1 style="margin: 0; font-size: 24px;">🏥 MediCare+ Medical Insurance Report</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">AI-Powered Insurance Analysis</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">{prediction_amount}</div>
                    <div style="opacity: 0.9;">Confidence: {confidence}% | {timestamp}</div>
                </div>
                
                <div style="margin-bottom: 25px;">
                    <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px;">📋 Patient Details</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                            <strong>Age:</strong> {patient_data.get('age')} years
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                            <strong>BMI:</strong> {patient_data.get('bmi')}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                            <strong>Gender:</strong> {patient_data.get('gender')}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                            <strong>Smoker:</strong> {patient_data.get('smoker')}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                            <strong>Region:</strong> {patient_data.get('region')}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                            <strong>Premium:</strong> ₹{patient_data.get('premium_annual_inr', 'N/A')}
                        </div>
                    </div>
                </div>
                
                <div style="background: #e9ecef; padding: 15px; border-radius: 5px; font-size: 12px; color: #666;">
                    <strong>⚠️ Disclaimer:</strong> This AI prediction is for informational purposes only. 
                    Consult healthcare professionals for medical decisions.
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                    <p><strong>MediCare+ Platform</strong> | Generated: {timestamp}</p>
                    <p>Report sent to: {recipient_email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        return {
            "message": msg,
            "recipient": recipient_email,
            "subject": msg['Subject']
        }
    
    def format_currency(self, value: float) -> str:
        """Format currency in Indian Rupees"""
        return f"₹{value:,.0f}"

# Create global instance
bulletproof_email_service = BulletproofEmailService()

# Test function
async def test_bulletproof_service():
    """Test the bulletproof email service"""
    print("🧪 TESTING BULLETPROOF EMAIL SERVICE")
    print("="*80)
    
    # Test connection
    connection_result = bulletproof_email_service.test_gmail_connection()
    print(f"\n🔗 Connection Test: {'✅ PASS' if connection_result['success'] else '❌ FAIL'}")
    
    if not connection_result['success']:
        print(f"❌ Error: {connection_result['message']}")
        if 'details' in connection_result:
            print(f"Details: {connection_result['details']}")
        return
    
    # Test email sending
    test_email = "gowthaamankrishna1998@gmail.com"  # User's email
    test_prediction = {"prediction": 25000, "confidence": 0.88}
    test_patient_data = {
        "age": 28, "bmi": 24.5, "gender": "Male", "smoker": "No", 
        "region": "South", "premium_annual_inr": 22000
    }
    
    print(f"\n📧 Testing email to: {test_email}")
    result = await bulletproof_email_service.send_prediction_email(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data
    )
    
    print(f"\n📊 Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
    else:
        if 'details' in result:
            print(f"Details: {result['details']}")

if __name__ == "__main__":
    asyncio.run(test_bulletproof_service())
