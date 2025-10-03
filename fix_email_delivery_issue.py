#!/usr/bin/env python3
"""
Fix Email Delivery Issue - MediCare+ Platform
Resolves false success messages when emails aren't actually delivered to Gmail
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import asyncio
import json
from typing import Dict, Any
import socket
import time

class FixedEmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_EMAIL")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD")
        self.sender_name = "MediCare+ Platform"
        
        # Check if credentials are properly configured
        self.email_enabled = bool(self.sender_email and self.sender_password)
        
        # Timeout settings
        self.connection_timeout = 15
        self.send_timeout = 30
        self.total_timeout = 45
        
        print("="*60)
        print("🔧 FIXED EMAIL SERVICE INITIALIZATION")
        print("="*60)
        print(f"Gmail Email: {self.sender_email if self.sender_email else '❌ NOT SET'}")
        print(f"Gmail App Password: {'✅ SET' if self.sender_password else '❌ NOT SET'}")
        print(f"Email Service Enabled: {'✅ YES' if self.email_enabled else '❌ NO'}")
        print("="*60)
        
        if not self.email_enabled:
            print("⚠️ EMAIL SERVICE DISABLED")
            print("💡 Required environment variables:")
            print("   - GMAIL_EMAIL: Your Gmail address")
            print("   - GMAIL_APP_PASSWORD: Your Gmail App Password")
            print("   - Make sure these are set in your Render environment variables")
    
    def test_gmail_connection(self) -> Dict[str, Any]:
        """Test Gmail SMTP connection and authentication"""
        if not self.email_enabled:
            return {
                "success": False,
                "error": "Gmail credentials not configured",
                "details": "GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables are required"
            }
        
        try:
            print("🔗 Testing Gmail SMTP connection...")
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Test connection
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
                print("✅ Connected to Gmail SMTP server")
                
                # Test TLS
                server.starttls(context=context)
                print("✅ TLS encryption established")
                
                # Test authentication
                server.login(self.sender_email, self.sender_password)
                print("✅ Gmail authentication successful")
                
                return {
                    "success": True,
                    "message": "Gmail connection and authentication successful",
                    "smtp_server": self.smtp_server,
                    "sender_email": self.sender_email
                }
                
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Gmail authentication failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": "Authentication failed",
                "details": error_msg,
                "fix_instructions": [
                    "1. Verify GMAIL_EMAIL is correct",
                    "2. Generate new Gmail App Password",
                    "3. Update GMAIL_APP_PASSWORD in Render environment",
                    "4. Make sure 2FA is enabled on Gmail account"
                ]
            }
            
        except smtplib.SMTPConnectError as e:
            error_msg = f"Cannot connect to Gmail SMTP server: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": "Connection failed",
                "details": error_msg
            }
            
        except Exception as e:
            error_msg = f"Gmail connection test failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": "Unknown error",
                "details": error_msg
            }
    
    async def send_prediction_email_with_honest_feedback(
        self, 
        recipient_email: str, 
        prediction_data: Dict[str, Any], 
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send email with HONEST feedback - only returns success if email actually reaches Gmail
        """
        start_time = time.time()
        
        print(f"📧 HONEST EMAIL SEND to {recipient_email}")
        print("-" * 50)
        
        # Step 1: Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, recipient_email):
            return {
                "success": False,
                "message": f"❌ Invalid email format: {recipient_email}",
                "error_type": "validation"
            }
        
        # Step 2: Check if email service is configured
        if not self.email_enabled:
            return {
                "success": False,
                "message": "❌ Email service is not configured. Gmail credentials (GMAIL_EMAIL and GMAIL_APP_PASSWORD) are required.",
                "error_type": "not_configured",
                "fix_instructions": [
                    "1. Set GMAIL_EMAIL environment variable",
                    "2. Set GMAIL_APP_PASSWORD environment variable", 
                    "3. Restart the application"
                ]
            }
        
        # Step 3: Test Gmail connection first
        connection_test = self.test_gmail_connection()
        if not connection_test["success"]:
            return {
                "success": False,
                "message": f"❌ Gmail connection failed: {connection_test['error']}",
                "error_type": "connection_failed",
                "details": connection_test.get("details", ""),
                "fix_instructions": connection_test.get("fix_instructions", [])
            }
        
        # Step 4: Prepare email content
        try:
            email_content = self._prepare_professional_email(prediction_data, patient_data, recipient_email)
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Failed to prepare email content: {str(e)}",
                "error_type": "content_preparation"
            }
        
        # Step 5: Actually send the email
        try:
            print("📤 Sending email to Gmail...")
            
            # Set socket timeout
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.total_timeout)
            
            try:
                # Send email with strict error checking
                await self._send_email_with_verification(email_content, recipient_email)
                
                processing_time = round(time.time() - start_time, 2)
                success_message = f"✅ Email sent successfully to {recipient_email}! Check your inbox (including spam folder)."
                
                print(f"✅ EMAIL DELIVERED in {processing_time}s")
                
                # Store successful delivery record
                await self._store_delivery_record(recipient_email, "delivered", processing_time)
                
                return {
                    "success": True,
                    "message": success_message,
                    "processing_time": processing_time,
                    "delivery_status": "delivered"
                }
                
            finally:
                socket.setdefaulttimeout(original_timeout)
                
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ Gmail authentication failed: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": "❌ Gmail authentication failed. Please check your Gmail App Password configuration.",
                "error_type": "authentication",
                "details": str(e)
            }
            
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"❌ Recipient email refused: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": f"❌ The email address {recipient_email} was rejected by Gmail. Please check the email address.",
                "error_type": "recipient_refused",
                "details": str(e)
            }
            
        except smtplib.SMTPException as e:
            error_msg = f"❌ SMTP error: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": f"❌ Email sending failed due to SMTP error: {str(e)}",
                "error_type": "smtp_error",
                "details": str(e)
            }
            
        except asyncio.TimeoutError:
            error_msg = f"❌ Email sending timed out after {self.total_timeout} seconds"
            print(error_msg)
            return {
                "success": False,
                "message": f"❌ Email sending timed out. Please try again or check your internet connection.",
                "error_type": "timeout",
                "timeout_duration": self.total_timeout
            }
            
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": f"❌ Email sending failed: {str(e)}",
                "error_type": "unknown",
                "details": str(e)
            }
    
    async def _send_email_with_verification(self, email_content: Dict, recipient_email: str):
        """Send email with proper verification"""
        loop = asyncio.get_event_loop()
        
        def send_sync():
            # Create optimized SSL context
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
                # Enable debug output for troubleshooting
                # server.set_debuglevel(1)
                
                print("🔐 Starting TLS...")
                server.starttls(context=context)
                
                print("🔑 Authenticating with Gmail...")
                server.login(self.sender_email, self.sender_password)
                
                print("📧 Sending email...")
                # Send email and get response
                result = server.sendmail(
                    from_addr=self.sender_email,
                    to_addrs=[recipient_email],
                    msg=email_content["message"].as_string()
                )
                
                # Check if there were any rejected recipients
                if result:
                    raise smtplib.SMTPRecipientsRefused(result)
                
                print("✅ Email sent to Gmail successfully")
        
        # Run in executor with timeout
        await asyncio.wait_for(
            loop.run_in_executor(None, send_sync),
            timeout=self.total_timeout
        )
    
    def _prepare_professional_email(self, prediction_data: Dict, patient_data: Dict, recipient_email: str) -> Dict:
        """Prepare professional email content"""
        prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
        confidence = round(prediction_data.get('confidence', 0) * 100, 1)
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
        
        # Create email message with proper headers
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏥 MediCare+ Medical Insurance Report - {prediction_amount}"
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['To'] = recipient_email
        msg['Reply-To'] = self.sender_email
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0530')
        msg['Message-ID'] = f"<{datetime.now().strftime('%Y%m%d%H%M%S')}.{recipient_email.replace('@', '_at_')}@medicare-plus.com>"
        
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
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Professional AI-Powered Insurance Claim Analysis</p>
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
                    <strong>⚠️ Medical Disclaimer:</strong> This AI-generated prediction is for educational and informational purposes only. 
                    It should not be used as a substitute for professional medical advice, diagnosis, or treatment. 
                    Always consult with qualified healthcare providers for medical decisions.
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px;">
                    <p><strong>MediCare+ AI Platform</strong> | © 2024 MediCare+ Healthcare Technology</p>
                    <p>Powered by Advanced Machine Learning & Medical Data Analytics</p>
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
    
    async def _store_delivery_record(self, recipient_email: str, status: str, processing_time: float):
        """Store delivery record for tracking"""
        try:
            record = {
                "recipient": recipient_email,
                "status": status,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "service": "fixed_email_service"
            }
            
            records_file = "email_delivery_records.json"
            records = []
            
            if os.path.exists(records_file):
                try:
                    with open(records_file, 'r') as f:
                        records = json.load(f)
                except:
                    records = []
            
            records.append(record)
            
            # Keep only last 50 records
            if len(records) > 50:
                records = records[-50:]
            
            with open(records_file, 'w') as f:
                json.dump(records, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Failed to store delivery record: {e}")
    
    def format_currency(self, value: float) -> str:
        """Format currency in Indian Rupees"""
        return f"₹{value:,.0f}"

# Test function
async def test_fixed_email_service():
    """Test the fixed email service"""
    print("🧪 TESTING FIXED EMAIL SERVICE")
    print("="*60)
    
    service = FixedEmailService()
    
    # Test Gmail connection
    connection_result = service.test_gmail_connection()
    print(f"Connection Test: {'✅ PASS' if connection_result['success'] else '❌ FAIL'}")
    
    if not connection_result['success']:
        print("❌ Gmail connection failed:")
        print(f"   Error: {connection_result['error']}")
        print(f"   Details: {connection_result.get('details', 'N/A')}")
        if 'fix_instructions' in connection_result:
            print("   Fix Instructions:")
            for instruction in connection_result['fix_instructions']:
                print(f"     {instruction}")
        return
    
    # Test email sending
    test_email = "perivihari8@gmail.com"  # Use the email from the user's request
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
    result = await service.send_prediction_email_with_honest_feedback(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data
    )
    
    print(f"\nResult: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    
    if not result['success']:
        print(f"Error Type: {result.get('error_type', 'unknown')}")
        if 'details' in result:
            print(f"Details: {result['details']}")
        if 'fix_instructions' in result:
            print("Fix Instructions:")
            for instruction in result['fix_instructions']:
                print(f"  {instruction}")

if __name__ == "__main__":
    asyncio.run(test_fixed_email_service())
