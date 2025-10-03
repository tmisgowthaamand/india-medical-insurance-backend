#!/usr/bin/env python3
"""
Render-Optimized Email Service for MediCare+ Platform
Fixes Gmail connection issues on Render deployment with proper environment variable handling
"""

import os
import smtplib
import ssl
import asyncio
import time
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any
import re

class RenderEmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Read environment variables with proper fallbacks
        self.sender_email = os.getenv("GMAIL_EMAIL")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD")
        self.sender_name = "MediCare+ Platform"
        
        # Check if credentials are available
        self.email_enabled = bool(self.sender_email and self.sender_password)
        
        # Optimized timeout settings for Render
        self.connection_timeout = 20
        self.send_timeout = 30
        self.total_timeout = 60
        
        print("="*70)
        print("🚀 RENDER EMAIL SERVICE - MediCare+ Platform")
        print("="*70)
        print(f"📧 Gmail Email: {self.sender_email if self.sender_email else '❌ NOT SET'}")
        print(f"🔑 App Password: {'✅ SET' if self.sender_password else '❌ NOT SET'}")
        print(f"🌐 Email Service: {'✅ ENABLED' if self.email_enabled else '❌ DISABLED'}")
        print("="*70)
        
        if not self.email_enabled:
            print("⚠️ EMAIL SERVICE DISABLED - Missing environment variables:")
            print("   Required: GMAIL_EMAIL and GMAIL_APP_PASSWORD")
            print("   Please set these in your Render environment variables")
    
    def test_gmail_connection(self) -> Dict[str, Any]:
        """Test Gmail SMTP connection with detailed error reporting"""
        print("🔗 Testing Gmail SMTP connection...")
        
        if not self.email_enabled:
            return {
                "success": False,
                "error": "Credentials not configured",
                "message": "❌ Gmail connection failed: GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables are required"
            }
        
        try:
            # Set socket timeout
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.connection_timeout)
            
            try:
                # Create SSL context
                context = ssl.create_default_context()
                
                print(f"   📡 Connecting to {self.smtp_server}:{self.smtp_port}...")
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
                    print("   ✅ Connected to Gmail SMTP server")
                    
                    print("   🔐 Starting TLS encryption...")
                    server.starttls(context=context)
                    print("   ✅ TLS encryption established")
                    
                    print("   🔑 Authenticating with Gmail...")
                    server.login(self.sender_email, self.sender_password)
                    print("   ✅ Gmail authentication successful")
                    
                    return {
                        "success": True,
                        "message": "✅ Gmail connection successful",
                        "smtp_server": f"{self.smtp_server}:{self.smtp_port}",
                        "sender_email": self.sender_email
                    }
                    
            finally:
                socket.setdefaulttimeout(original_timeout)
                
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "❌ Gmail connection failed: Authentication failed"
            print(f"   {error_msg}")
            print(f"   Details: {str(e)}")
            return {
                "success": False,
                "error": "Authentication failed",
                "message": error_msg,
                "details": str(e),
                "fix_instructions": [
                    "1. Verify GMAIL_EMAIL is correct in Render environment",
                    "2. Generate new Gmail App Password",
                    "3. Update GMAIL_APP_PASSWORD in Render environment",
                    "4. Ensure 2FA is enabled on Gmail account"
                ]
            }
            
        except smtplib.SMTPConnectError as e:
            error_msg = "❌ Gmail connection failed: Cannot connect to server"
            print(f"   {error_msg}")
            print(f"   Details: {str(e)}")
            return {
                "success": False,
                "error": "Connection failed",
                "message": error_msg,
                "details": str(e)
            }
            
        except socket.timeout:
            error_msg = "❌ Gmail connection failed: Connection timeout"
            print(f"   {error_msg}")
            return {
                "success": False,
                "error": "Timeout",
                "message": error_msg,
                "details": f"Connection timed out after {self.connection_timeout} seconds"
            }
            
        except Exception as e:
            error_msg = "❌ Gmail connection failed: Unknown error"
            print(f"   {error_msg}")
            print(f"   Details: {str(e)}")
            return {
                "success": False,
                "error": "Unknown error",
                "message": error_msg,
                "details": str(e)
            }
    
    async def send_prediction_email(self, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> Dict[str, Any]:
        """Send prediction email with verified delivery"""
        start_time = time.time()
        
        print(f"📧 SENDING PREDICTION EMAIL TO: {recipient_email}")
        print("-" * 50)
        
        # Step 1: Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, recipient_email):
            return {
                "success": False,
                "message": f"❌ Invalid email format: {recipient_email}"
            }
        
        # Step 2: Check if email service is enabled
        if not self.email_enabled:
            return {
                "success": False,
                "message": "❌ Email service is not configured. Please set GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables in Render."
            }
        
        # Step 3: Test Gmail connection first
        connection_test = self.test_gmail_connection()
        if not connection_test["success"]:
            return {
                "success": False,
                "message": connection_test["message"],
                "error_type": connection_test["error"],
                "details": connection_test.get("details", ""),
                "fix_instructions": connection_test.get("fix_instructions", [])
            }
        
        # Step 4: Prepare and send email
        try:
            email_content = self._prepare_prediction_email(prediction_data, patient_data, recipient_email)
            
            print("📤 Sending email to Gmail...")
            await self._send_email_verified(email_content, recipient_email)
            
            processing_time = round(time.time() - start_time, 2)
            success_message = f"✅ Email sent successfully to {recipient_email}! Check your inbox (including spam folder)."
            
            print(f"✅ EMAIL DELIVERED in {processing_time}s")
            
            return {
                "success": True,
                "message": success_message,
                "processing_time": processing_time,
                "delivery_status": "delivered",
                "recipient": recipient_email
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "❌ Gmail authentication failed during send"
            print(f"   {error_msg}: {str(e)}")
            return {
                "success": False,
                "message": "❌ Gmail authentication failed. Please check your Gmail App Password configuration in Render environment variables."
            }
            
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"❌ Recipient email refused: {str(e)}"
            print(f"   {error_msg}")
            return {
                "success": False,
                "message": f"❌ The email address {recipient_email} was rejected by Gmail. Please check the email address."
            }
            
        except asyncio.TimeoutError:
            error_msg = f"❌ Email sending timed out after {self.total_timeout} seconds"
            print(f"   {error_msg}")
            return {
                "success": False,
                "message": "❌ Email sending timed out. Please try again or check your internet connection."
            }
            
        except Exception as e:
            error_msg = f"❌ Email sending failed: {str(e)}"
            print(f"   {error_msg}")
            return {
                "success": False,
                "message": f"❌ Email sending failed: {str(e)}"
            }
    
    async def _send_email_verified(self, email_content: Dict, recipient_email: str):
        """Send email with proper verification and timeout handling"""
        loop = asyncio.get_event_loop()
        
        def send_sync():
            # Set socket timeout
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.send_timeout)
            
            try:
                # Create SSL context
                context = ssl.create_default_context()
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
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
                    
                    # Check if there were any rejected recipients
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
    
    def _prepare_prediction_email(self, prediction_data: Dict, patient_data: Dict, recipient_email: str) -> Dict:
        """Prepare professional email content"""
        prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
        confidence = round(prediction_data.get('confidence', 0) * 100, 1)
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏥 MediCare+ Medical Insurance Report - {prediction_amount}"
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['To'] = recipient_email
        msg['Reply-To'] = self.sender_email
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0530')
        
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
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">AI-Powered Insurance Claim Analysis</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">{prediction_amount}</div>
                    <div style="opacity: 0.9;">Confidence: {confidence}% | Generated: {timestamp}</div>
                </div>
                
                <div style="margin-bottom: 25px;">
                    <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px; margin-bottom: 15px;">📋 Patient Information</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">Age</strong>
                            {patient_data.get('age')} years
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">BMI</strong>
                            {patient_data.get('bmi')}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">Gender</strong>
                            {patient_data.get('gender')}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">Smoking Status</strong>
                            {patient_data.get('smoker')}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">Region</strong>
                            {patient_data.get('region')}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">Annual Premium</strong>
                            ₹{patient_data.get('premium_annual_inr', 'Estimated')}
                        </div>
                    </div>
                </div>
                
                <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #666;">
                    <strong>⚠️ Medical Disclaimer:</strong> This AI-generated prediction is for educational purposes only. 
                    Always consult with qualified healthcare providers for medical decisions.
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px;">
                    <p><strong>MediCare+ AI Platform</strong> | © 2024 MediCare+ Healthcare Technology</p>
                    <p>Report generated on {timestamp} for {recipient_email}</p>
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
render_email_service = RenderEmailService()

# Test function
async def test_render_email_service():
    """Test the render email service"""
    print("🧪 TESTING RENDER EMAIL SERVICE")
    print("="*70)
    
    # Test Gmail connection
    connection_result = render_email_service.test_gmail_connection()
    print(f"Connection Test: {'✅ PASS' if connection_result['success'] else '❌ FAIL'}")
    
    if not connection_result['success']:
        print("❌ Gmail connection failed:")
        print(f"   Error: {connection_result['error']}")
        print(f"   Message: {connection_result['message']}")
        if 'details' in connection_result:
            print(f"   Details: {connection_result['details']}")
        if 'fix_instructions' in connection_result:
            print("   Fix Instructions:")
            for instruction in connection_result['fix_instructions']:
                print(f"     {instruction}")
        return
    
    # Test email sending
    test_email = "perivihari8@gmail.com"
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
    
    print(f"\n📧 Testing email send to: {test_email}")
    result = await render_email_service.send_prediction_email(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data
    )
    
    print(f"\nResult: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    
    if not result['success']:
        if 'error_type' in result:
            print(f"Error Type: {result['error_type']}")
        if 'details' in result:
            print(f"Details: {result['details']}")
        if 'fix_instructions' in result:
            print("Fix Instructions:")
            for instruction in result['fix_instructions']:
                print(f"  {instruction}")

if __name__ == "__main__":
    asyncio.run(test_render_email_service())
