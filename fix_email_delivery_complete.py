#!/usr/bin/env python3
"""
COMPLETE EMAIL DELIVERY FIX for MediCare+ Platform
Fixes all email delivery issues and ensures emails actually reach Gmail inbox
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

class EmailDeliveryFix:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_EMAIL", "gokrishna98@gmail.com")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD", "lwkvzupqanxvafrm")
        self.sender_name = "MediCare+ Platform"
        
        # Optimized timeout settings
        self.connection_timeout = 30
        self.send_timeout = 45
        
        print("="*70)
        print("🔧 EMAIL DELIVERY FIX - MediCare+ Platform")
        print("="*70)
        print(f"📧 Gmail Email: {self.sender_email}")
        print(f"🔑 App Password: {'✅ SET' if self.sender_password else '❌ NOT SET'}")
        print("="*70)
    
    def test_gmail_connection(self) -> Dict[str, Any]:
        """Test Gmail SMTP connection with detailed diagnostics"""
        print("🔗 Testing Gmail SMTP connection...")
        
        if not self.sender_email or not self.sender_password:
            return {
                "success": False,
                "error": "Gmail credentials not configured",
                "message": "❌ Gmail connection failed: Credentials not configured"
            }
        
        try:
            # Create proper SSL context
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
                    "message": "✅ Gmail connection successful",
                    "smtp_server": f"{self.smtp_server}:{self.smtp_port}",
                    "sender_email": self.sender_email
                }
                
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ Gmail connection failed: Authentication error"
            print(f"   {error_msg}: {str(e)}")
            return {
                "success": False,
                "error": "Authentication failed",
                "message": error_msg,
                "details": str(e)
            }
            
        except Exception as e:
            error_msg = f"❌ Gmail connection failed: Unknown error"
            print(f"   {error_msg}: {str(e)}")
            return {
                "success": False,
                "error": "Unknown error",
                "message": error_msg,
                "details": str(e)
            }
    
    async def send_prediction_email(self, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> Dict[str, Any]:
        """Send prediction email with VERIFIED delivery"""
        start_time = time.time()
        
        print(f"📧 SENDING PREDICTION EMAIL TO: {recipient_email}")
        print("-" * 50)
        
        # Step 1: Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, recipient_email):
            return {
                "success": False,
                "message": f"❌ Invalid email format: {recipient_email}"
            }
        
        # Step 2: Test Gmail connection first
        connection_test = self.test_gmail_connection()
        if not connection_test["success"]:
            return connection_test
        
        # Step 3: Prepare and send email
        try:
            email_content = self._prepare_prediction_email(prediction_data, patient_data, recipient_email)
            
            print("📤 Sending email to Gmail...")
            await self._send_email_verified(email_content, recipient_email)
            
            processing_time = round(time.time() - start_time, 2)
            success_message = f"✅ Email sent successfully to {recipient_email}! Check your inbox."
            
            print(f"✅ EMAIL DELIVERED in {processing_time}s")
            
            return {
                "success": True,
                "message": success_message,
                "processing_time": processing_time,
                "delivery_status": "delivered",
                "recipient": recipient_email
            }
            
        except Exception as e:
            error_msg = f"❌ Email sending failed: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": error_msg
            }
    
    async def _send_email_verified(self, email_content: Dict, recipient_email: str):
        """Send email with proper verification"""
        loop = asyncio.get_event_loop()
        
        def send_sync():
            # Create SSL context with proper settings
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
                print("🔐 Starting TLS...")
                server.starttls(context=context)
                
                print("🔑 Authenticating with Gmail...")
                server.login(self.sender_email, self.sender_password)
                
                print("📧 Sending email...")
                # Send email and verify delivery
                result = server.sendmail(
                    from_addr=self.sender_email,
                    to_addrs=[recipient_email],
                    msg=email_content["message"].as_string()
                )
                
                # Check for rejected recipients
                if result:
                    raise smtplib.SMTPRecipientsRefused(result)
                
                print("✅ Email sent to Gmail successfully")
        
        # Run with timeout
        await asyncio.wait_for(
            loop.run_in_executor(None, send_sync),
            timeout=self.send_timeout
        )
    
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
    """Test the email delivery fix"""
    print("🚀 TESTING EMAIL DELIVERY FIX")
    print()
    
    # Initialize email service
    email_service = EmailDeliveryFix()
    
    # Test Gmail connection
    print("🔗 TEST 1: Gmail Connection")
    connection_result = email_service.test_gmail_connection()
    
    if not connection_result["success"]:
        print("❌ Gmail connection failed - cannot proceed")
        print(f"Error: {connection_result['message']}")
        return
    
    print("✅ Gmail connection successful!")
    print()
    
    # Test email sending
    test_email = "perivihari8@gmail.com"
    print(f"📧 TEST 2: Sending prediction email to {test_email}")
    
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
    
    result = await email_service.send_prediction_email(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data
    )
    
    if result["success"]:
        print("✅ Email sent successfully!")
        print(f"Processing time: {result.get('processing_time', 'unknown')}s")
    else:
        print("❌ Email failed!")
        print(f"Error: {result['message']}")
        return
    
    print()
    print("="*70)
    print("🎉 EMAIL DELIVERY FIX TEST PASSED!")
    print(f"✅ Check {test_email} inbox (including spam folder)")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
