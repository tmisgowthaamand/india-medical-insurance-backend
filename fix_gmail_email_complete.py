#!/usr/bin/env python3
"""
Complete Gmail Email Fix for MediCare+ Platform
Fixes email delivery issues and ensures emails reach users successfully
"""

import os
import smtplib
import ssl
import asyncio
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CompleteEmailFix:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_EMAIL", "gokrishna98@gmail.com")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD", "lwkvzupqanxvafrm")
        self.sender_name = "MediCare+ Platform"
        
        # Timeout settings optimized for Gmail
        self.connection_timeout = 20
        self.send_timeout = 30
        self.total_timeout = 60
        
        print("="*70)
        print("🔧 COMPLETE GMAIL EMAIL FIX - MediCare+ Platform")
        print("="*70)
        print(f"📧 Gmail Email: {self.sender_email}")
        print(f"🔑 App Password: {'✅ SET (' + self.sender_password[:4] + '****' + self.sender_password[-4:] + ')' if self.sender_password else '❌ NOT SET'}")
        print(f"🌐 SMTP Server: {self.smtp_server}:{self.smtp_port}")
        print("="*70)
    
    def test_gmail_connection(self) -> Dict[str, Any]:
        """Test Gmail SMTP connection with detailed diagnostics"""
        print("🔗 Testing Gmail SMTP connection...")
        
        if not self.sender_email or not self.sender_password:
            return {
                "success": False,
                "error": "Gmail credentials not configured",
                "details": "GMAIL_EMAIL and GMAIL_APP_PASSWORD are required"
            }
        
        try:
            # Create SSL context with proper settings
            context = ssl.create_default_context()
            
            print("   📡 Connecting to Gmail SMTP server...")
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
                    "message": "Gmail connection and authentication successful",
                    "smtp_server": f"{self.smtp_server}:{self.smtp_port}",
                    "sender_email": self.sender_email
                }
                
        except smtplib.SMTPAuthenticationError as e:
            error_details = str(e)
            print(f"   ❌ Gmail authentication failed: {error_details}")
            
            fix_instructions = [
                "1. Verify GMAIL_EMAIL is correct: " + self.sender_email,
                "2. Check if 2-Factor Authentication is enabled on Gmail account",
                "3. Generate new Gmail App Password:",
                "   - Go to https://myaccount.google.com/security",
                "   - Click 'App passwords' (requires 2FA)",
                "   - Generate password for 'Mail' application",
                "   - Use the 16-character password (no spaces)",
                "4. Update GMAIL_APP_PASSWORD environment variable",
                "5. Restart the application"
            ]
            
            return {
                "success": False,
                "error": "Authentication failed",
                "details": error_details,
                "fix_instructions": fix_instructions
            }
            
        except smtplib.SMTPConnectError as e:
            error_details = str(e)
            print(f"   ❌ Cannot connect to Gmail SMTP: {error_details}")
            return {
                "success": False,
                "error": "Connection failed",
                "details": error_details,
                "fix_instructions": [
                    "1. Check internet connection",
                    "2. Verify firewall settings allow SMTP (port 587)",
                    "3. Try again in a few minutes"
                ]
            }
            
        except Exception as e:
            error_details = str(e)
            print(f"   ❌ Gmail connection test failed: {error_details}")
            return {
                "success": False,
                "error": "Unknown error",
                "details": error_details
            }
    
    async def send_test_email(self, recipient_email: str) -> Dict[str, Any]:
        """Send a test email with comprehensive error handling"""
        start_time = time.time()
        
        print(f"📧 SENDING TEST EMAIL TO: {recipient_email}")
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
        
        # Step 2: Test Gmail connection first
        connection_test = self.test_gmail_connection()
        if not connection_test["success"]:
            return {
                "success": False,
                "message": f"❌ Gmail connection failed: {connection_test['error']}",
                "error_type": "connection_failed",
                "details": connection_test.get("details", ""),
                "fix_instructions": connection_test.get("fix_instructions", [])
            }
        
        # Step 3: Prepare test email content
        try:
            email_content = self._prepare_test_email(recipient_email)
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Failed to prepare email content: {str(e)}",
                "error_type": "content_preparation"
            }
        
        # Step 4: Send the email
        try:
            print("📤 Sending email to Gmail...")
            
            await self._send_email_with_verification(email_content, recipient_email)
            
            processing_time = round(time.time() - start_time, 2)
            success_message = f"✅ Test email sent successfully to {recipient_email}! Check your inbox (including spam folder)."
            
            print(f"✅ EMAIL DELIVERED in {processing_time}s")
            
            return {
                "success": True,
                "message": success_message,
                "processing_time": processing_time,
                "delivery_status": "delivered",
                "recipient": recipient_email
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ Gmail authentication failed: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": "❌ Gmail authentication failed. Please check your Gmail App Password.",
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
            
        except Exception as e:
            error_msg = f"❌ Email sending failed: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": f"❌ Email sending failed: {str(e)}",
                "error_type": "send_failed",
                "details": str(e)
            }
    
    async def _send_email_with_verification(self, email_content: Dict, recipient_email: str):
        """Send email with proper verification"""
        loop = asyncio.get_event_loop()
        
        def send_sync():
            # Create SSL context
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
                print("🔐 Starting TLS...")
                server.starttls(context=context)
                
                print("🔑 Authenticating with Gmail...")
                server.login(self.sender_email, self.sender_password)
                
                print("📧 Sending email...")
                # Send email and check for errors
                result = server.sendmail(
                    from_addr=self.sender_email,
                    to_addrs=[recipient_email],
                    msg=email_content["message"].as_string()
                )
                
                # Check if there were any rejected recipients
                if result:
                    raise smtplib.SMTPRecipientsRefused(result)
                
                print("✅ Email sent to Gmail successfully")
        
        # Run with timeout
        await asyncio.wait_for(
            loop.run_in_executor(None, send_sync),
            timeout=self.total_timeout
        )
    
    def _prepare_test_email(self, recipient_email: str) -> Dict:
        """Prepare test email content"""
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🏥 MediCare+ Email Test - Gmail Delivery Verification"
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
            <title>MediCare+ Email Test</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px;">
                    <h1 style="margin: 0; font-size: 24px;">🏥 MediCare+ Email Test</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Gmail Delivery Verification</p>
                </div>
                
                <div style="background: #e8f5e8; border-left: 4px solid #28a745; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h2 style="color: #28a745; margin: 0 0 10px 0;">✅ Email Delivery Successful!</h2>
                    <p style="margin: 0;">This test email confirms that the MediCare+ email system is working correctly and can deliver emails to your Gmail inbox.</p>
                </div>
                
                <div style="margin-bottom: 25px;">
                    <h3 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px;">📋 Test Details</h3>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <p><strong>Recipient:</strong> {recipient_email}</p>
                        <p><strong>Sender:</strong> {self.sender_email}</p>
                        <p><strong>Test Time:</strong> {timestamp}</p>
                        <p><strong>SMTP Server:</strong> {self.smtp_server}:{self.smtp_port}</p>
                        <p><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">✅ DELIVERED</span></p>
                    </div>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h4 style="color: #856404; margin: 0 0 10px 0;">📧 What This Means</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #856404;">
                        <li>Your Gmail credentials are properly configured</li>
                        <li>The MediCare+ email system is working correctly</li>
                        <li>You will now receive prediction reports via email</li>
                        <li>Check your spam folder if emails don't appear in inbox</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px;">
                    <p><strong>MediCare+ AI Platform</strong> | © 2024 MediCare+ Healthcare Technology</p>
                    <p>Email Test completed on {timestamp}</p>
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
    
    async def send_prediction_email(self, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> Dict[str, Any]:
        """Send prediction email with medical report"""
        start_time = time.time()
        
        print(f"📧 SENDING PREDICTION EMAIL TO: {recipient_email}")
        print("-" * 50)
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, recipient_email):
            return {
                "success": False,
                "message": f"❌ Invalid email format: {recipient_email}",
                "error_type": "validation"
            }
        
        # Test connection first
        connection_test = self.test_gmail_connection()
        if not connection_test["success"]:
            return {
                "success": False,
                "message": f"❌ Gmail connection failed: {connection_test['error']}",
                "error_type": "connection_failed",
                "details": connection_test.get("details", ""),
                "fix_instructions": connection_test.get("fix_instructions", [])
            }
        
        # Prepare prediction email content
        try:
            email_content = self._prepare_prediction_email(prediction_data, patient_data, recipient_email)
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Failed to prepare email content: {str(e)}",
                "error_type": "content_preparation"
            }
        
        # Send the email
        try:
            print("📤 Sending prediction email...")
            
            await self._send_email_with_verification(email_content, recipient_email)
            
            processing_time = round(time.time() - start_time, 2)
            success_message = f"✅ Prediction email sent successfully to {recipient_email}!"
            
            print(f"✅ PREDICTION EMAIL DELIVERED in {processing_time}s")
            
            return {
                "success": True,
                "message": success_message,
                "processing_time": processing_time,
                "delivery_status": "delivered",
                "recipient": recipient_email
            }
            
        except Exception as e:
            error_msg = f"❌ Prediction email sending failed: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": f"❌ Prediction email sending failed: {str(e)}",
                "error_type": "send_failed",
                "details": str(e)
            }
    
    def _prepare_prediction_email(self, prediction_data: Dict, patient_data: Dict, recipient_email: str) -> Dict:
        """Prepare prediction email content"""
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
    
    def format_currency(self, value: float) -> str:
        """Format currency in Indian Rupees"""
        return f"₹{value:,.0f}"

async def main():
    """Main test function"""
    print("🚀 STARTING COMPLETE EMAIL FIX TEST")
    print()
    
    # Initialize email service
    email_service = CompleteEmailFix()
    
    # Test 1: Gmail Connection
    print("🔗 TEST 1: Gmail Connection")
    connection_result = email_service.test_gmail_connection()
    
    if not connection_result["success"]:
        print("❌ Gmail connection failed - cannot proceed with email tests")
        print(f"Error: {connection_result['error']}")
        if 'fix_instructions' in connection_result:
            print("\n🔧 FIX INSTRUCTIONS:")
            for instruction in connection_result['fix_instructions']:
                print(f"   {instruction}")
        return
    
    print("✅ Gmail connection successful!")
    print()
    
    # Test 2: Send test email to perivihari8@gmail.com
    test_email = "perivihari8@gmail.com"
    print(f"📧 TEST 2: Sending test email to {test_email}")
    
    test_result = await email_service.send_test_email(test_email)
    
    if test_result["success"]:
        print("✅ Test email sent successfully!")
        print(f"Processing time: {test_result.get('processing_time', 'unknown')}s")
    else:
        print("❌ Test email failed!")
        print(f"Error: {test_result['message']}")
        if 'fix_instructions' in test_result:
            print("\n🔧 FIX INSTRUCTIONS:")
            for instruction in test_result['fix_instructions']:
                print(f"   {instruction}")
        return
    
    print()
    
    # Test 3: Send prediction email
    print(f"📊 TEST 3: Sending prediction email to {test_email}")
    
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
    
    prediction_result = await email_service.send_prediction_email(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data
    )
    
    if prediction_result["success"]:
        print("✅ Prediction email sent successfully!")
        print(f"Processing time: {prediction_result.get('processing_time', 'unknown')}s")
    else:
        print("❌ Prediction email failed!")
        print(f"Error: {prediction_result['message']}")
        return
    
    print()
    print("="*70)
    print("🎉 ALL EMAIL TESTS PASSED!")
    print(f"✅ Check {test_email} inbox (including spam folder)")
    print("✅ Email functionality is working correctly")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
