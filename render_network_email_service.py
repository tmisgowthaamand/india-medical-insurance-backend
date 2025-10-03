#!/usr/bin/env python3
"""
Render Network-Aware Email Service for MediCare+ Platform
Handles Render network connectivity issues and Gmail storage functionality
"""

import os
import smtplib
import ssl
import asyncio
import time
import socket
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List
import re

class RenderNetworkEmailService:
    def __init__(self):
        # Multiple SMTP servers for fallback
        self.smtp_configs = [
            {"server": "smtp.gmail.com", "port": 587, "name": "Gmail Primary"},
            {"server": "smtp.gmail.com", "port": 465, "name": "Gmail SSL"},
            {"server": "smtp.gmail.com", "port": 25, "name": "Gmail Alt"}
        ]
        
        # Get credentials with fallbacks
        self.sender_email = self._get_email_credential()
        self.sender_password = self._get_password_credential()
        self.sender_name = "MediCare+ Platform"
        
        # Check if credentials are available
        self.email_enabled = bool(self.sender_email and self.sender_password)
        
        # Render-optimized timeout settings
        self.connection_timeout = 45
        self.send_timeout = 60
        self.total_timeout = 120
        
        # Gmail storage file
        self.gmail_storage_file = "user_emails.json"
        
        print("="*80)
        print("🌐 RENDER NETWORK EMAIL SERVICE - MediCare+ Platform")
        print("="*80)
        print(f"📧 Gmail Email: {self.sender_email if self.sender_email else '❌ NOT FOUND'}")
        print(f"🔑 App Password: {'✅ FOUND' if self.sender_password else '❌ NOT FOUND'}")
        print(f"🌐 Service Status: {'✅ READY' if self.email_enabled else '❌ DISABLED'}")
        print(f"🏗️ Environment: {'Render' if 'RENDER' in os.environ else 'Local'}")
        print(f"📁 Gmail Storage: {self.gmail_storage_file}")
        print("="*80)
        
        if not self.email_enabled:
            self._show_setup_instructions()
    
    def _get_email_credential(self):
        """Get email credential with multiple fallback methods"""
        email_vars = ["GMAIL_EMAIL", "EMAIL_USER", "SMTP_EMAIL", "SENDER_EMAIL"]
        
        for var in email_vars:
            email = os.getenv(var)
            if email:
                print(f"✅ Found email in {var}: {email}")
                return email
        
        # Fallback for Render
        fallback_email = "gokrishna98@gmail.com"
        print(f"⚠️ Using fallback email: {fallback_email}")
        return fallback_email
    
    def _get_password_credential(self):
        """Get password credential with multiple fallback methods"""
        password_vars = ["GMAIL_APP_PASSWORD", "EMAIL_PASSWORD", "SMTP_PASSWORD", "APP_PASSWORD"]
        
        for var in password_vars:
            password = os.getenv(var)
            if password:
                print(f"✅ Found password in {var}: {len(password)} chars")
                return password
        
        # Fallback for Render
        fallback_password = "lwkvzupqanxvafrm"
        print(f"⚠️ Using fallback password: {len(fallback_password)} chars")
        return fallback_password
    
    def _show_setup_instructions(self):
        """Show setup instructions"""
        print("🔧 RENDER EMAIL SERVICE SETUP")
        print("-" * 50)
        print("Set these environment variables in Render:")
        print("GMAIL_EMAIL=gokrishna98@gmail.com")
        print("GMAIL_APP_PASSWORD=lwkvzupqanxvafrm")
    
    def store_user_email(self, user_id: str, email: str) -> bool:
        """Store user's Gmail address for future use"""
        try:
            # Load existing data
            user_emails = {}
            if os.path.exists(self.gmail_storage_file):
                try:
                    with open(self.gmail_storage_file, 'r') as f:
                        user_emails = json.load(f)
                except:
                    user_emails = {}
            
            # Add or update user's emails
            if user_id not in user_emails:
                user_emails[user_id] = {
                    "emails": [],
                    "primary_email": email,
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            
            # Add email if not already present
            if email not in user_emails[user_id]["emails"]:
                user_emails[user_id]["emails"].append(email)
                user_emails[user_id]["last_updated"] = datetime.now().isoformat()
                
                # Set as primary if it's the first email
                if not user_emails[user_id]["primary_email"]:
                    user_emails[user_id]["primary_email"] = email
            
            # Save updated data
            with open(self.gmail_storage_file, 'w') as f:
                json.dump(user_emails, f, indent=2)
            
            print(f"✅ Stored email {email} for user {user_id}")
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to store user email: {e}")
            return False
    
    def get_user_emails(self, user_id: str) -> List[str]:
        """Get all emails for a user"""
        try:
            if os.path.exists(self.gmail_storage_file):
                with open(self.gmail_storage_file, 'r') as f:
                    user_emails = json.load(f)
                    if user_id in user_emails:
                        return user_emails[user_id].get("emails", [])
            return []
        except:
            return []
    
    def test_network_connectivity(self) -> Dict[str, Any]:
        """Test network connectivity for Render environment"""
        print("🌐 Testing Network Connectivity...")
        
        # Test 1: Basic internet connectivity
        try:
            print("   🔍 Testing basic internet connectivity...")
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=15)
            print("   ✅ Internet connection OK")
        except Exception as e:
            print(f"   ❌ Internet connection failed: {e}")
            return {
                "success": False,
                "error": "No internet",
                "message": "❌ No internet connection available on Render"
            }
        
        # Test 2: DNS resolution for Gmail
        try:
            print("   🔍 Testing Gmail DNS resolution...")
            for config in self.smtp_configs:
                try:
                    socket.gethostbyname(config["server"])
                    print(f"   ✅ {config['server']} resolved successfully")
                    break
                except Exception as e:
                    print(f"   ⚠️ {config['server']} resolution failed: {e}")
            else:
                return {
                    "success": False,
                    "error": "DNS failure",
                    "message": "❌ Cannot resolve Gmail SMTP servers"
                }
        except Exception as e:
            print(f"   ❌ DNS test failed: {e}")
            return {
                "success": False,
                "error": "DNS failure",
                "message": f"❌ DNS resolution failed: {str(e)}"
            }
        
        # Test 3: Port connectivity
        for config in self.smtp_configs:
            try:
                print(f"   🔍 Testing {config['name']} ({config['server']}:{config['port']})...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((config['server'], config['port']))
                sock.close()
                
                if result == 0:
                    print(f"   ✅ {config['name']} port {config['port']} is reachable")
                    return {
                        "success": True,
                        "message": "✅ Network connectivity OK",
                        "working_config": config
                    }
                else:
                    print(f"   ⚠️ {config['name']} port {config['port']} not reachable")
                    
            except Exception as e:
                print(f"   ⚠️ {config['name']} test failed: {e}")
        
        return {
            "success": False,
            "error": "Port blocked",
            "message": "❌ All Gmail SMTP ports are blocked on Render"
        }
    
    def test_gmail_connection(self) -> Dict[str, Any]:
        """Test Gmail connection with network awareness"""
        print("🔗 NETWORK-AWARE Gmail Connection Test")
        print("-" * 60)
        
        if not self.email_enabled:
            return {
                "success": False,
                "error": "Credentials missing",
                "message": "❌ Gmail credentials not configured"
            }
        
        # Test network connectivity first
        network_test = self.test_network_connectivity()
        if not network_test["success"]:
            return network_test
        
        # Try each SMTP configuration
        for config in self.smtp_configs:
            print(f"📡 Trying {config['name']} ({config['server']}:{config['port']})...")
            
            for attempt in range(2):
                try:
                    # Set socket timeout
                    original_timeout = socket.getdefaulttimeout()
                    socket.setdefaulttimeout(self.connection_timeout)
                    
                    try:
                        # Create SSL context
                        context = ssl.create_default_context()
                        if config['port'] == 465:
                            # SSL connection
                            with smtplib.SMTP_SSL(config['server'], config['port'], timeout=self.connection_timeout, context=context) as server:
                                print(f"   ✅ SSL connection established")
                                server.login(self.sender_email, self.sender_password)
                                print(f"   ✅ Authentication successful")
                                return {
                                    "success": True,
                                    "message": f"✅ Gmail connection successful via {config['name']}",
                                    "config": config
                                }
                        else:
                            # TLS connection
                            with smtplib.SMTP(config['server'], config['port'], timeout=self.connection_timeout) as server:
                                print(f"   ✅ Connected to {config['name']}")
                                server.starttls(context=context)
                                print(f"   ✅ TLS established")
                                server.login(self.sender_email, self.sender_password)
                                print(f"   ✅ Authentication successful")
                                return {
                                    "success": True,
                                    "message": f"✅ Gmail connection successful via {config['name']}",
                                    "config": config
                                }
                                
                    finally:
                        socket.setdefaulttimeout(original_timeout)
                        
                except Exception as e:
                    error_msg = str(e)
                    print(f"   ❌ {config['name']} attempt {attempt + 1} failed: {error_msg}")
                    
                    if attempt == 0:  # Retry once
                        print(f"   ⏳ Retrying {config['name']} in 3s...")
                        time.sleep(3)
        
        return {
            "success": False,
            "error": "All configs failed",
            "message": "❌ All Gmail SMTP configurations failed on Render network"
        }
    
    async def send_prediction_email(self, recipient_email: str, prediction_data: Dict, patient_data: Dict, user_id: str = None) -> Dict[str, Any]:
        """Send prediction email with Gmail storage"""
        start_time = time.time()
        
        print(f"📧 RENDER EMAIL SEND: {recipient_email}")
        print("-" * 60)
        
        # Step 1: Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, recipient_email):
            return {
                "success": False,
                "message": f"❌ Invalid email format: {recipient_email}"
            }
        
        # Step 2: Store user's Gmail (if user_id provided)
        if user_id:
            self.store_user_email(user_id, recipient_email)
        
        # Step 3: Check service availability
        if not self.email_enabled:
            return {
                "success": False,
                "message": "❌ Email service not configured on Render. Please set Gmail credentials."
            }
        
        # Step 4: Test connection
        connection_test = self.test_gmail_connection()
        if not connection_test["success"]:
            # Store the email attempt even if it fails
            if user_id:
                self._store_failed_email_attempt(user_id, recipient_email, connection_test["message"])
            
            return {
                "success": False,
                "message": connection_test["message"],
                "error_type": connection_test["error"],
                "details": connection_test.get("details", ""),
                "network_info": "Render network may be blocking Gmail SMTP ports"
            }
        
        # Step 5: Send email
        try:
            email_content = self._prepare_email_content(prediction_data, patient_data, recipient_email)
            
            # Use the working configuration from connection test
            working_config = connection_test.get("config", self.smtp_configs[0])
            
            await self._send_email_with_config(email_content, recipient_email, working_config)
            
            processing_time = round(time.time() - start_time, 2)
            success_message = f"✅ Email sent successfully to {recipient_email}! Check your Gmail inbox."
            
            print(f"🎉 EMAIL DELIVERED in {processing_time}s")
            
            # Store successful delivery
            if user_id:
                self._store_successful_email(user_id, recipient_email, processing_time)
            
            return {
                "success": True,
                "message": success_message,
                "processing_time": processing_time,
                "delivery_status": "delivered",
                "recipient": recipient_email,
                "config_used": working_config["name"]
            }
            
        except Exception as e:
            processing_time = round(time.time() - start_time, 2)
            error_msg = f"❌ Email sending failed: {str(e)}"
            print(error_msg)
            
            # Store failed attempt
            if user_id:
                self._store_failed_email_attempt(user_id, recipient_email, error_msg)
            
            return {
                "success": False,
                "message": error_msg,
                "processing_time": processing_time
            }
    
    async def _send_email_with_config(self, email_content: Dict, recipient_email: str, config: Dict):
        """Send email using specific SMTP configuration"""
        loop = asyncio.get_event_loop()
        
        def send_sync():
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.send_timeout)
            
            try:
                context = ssl.create_default_context()
                
                if config['port'] == 465:
                    # SSL connection
                    with smtplib.SMTP_SSL(config['server'], config['port'], timeout=self.connection_timeout, context=context) as server:
                        server.login(self.sender_email, self.sender_password)
                        result = server.sendmail(
                            from_addr=self.sender_email,
                            to_addrs=[recipient_email],
                            msg=email_content["message"].as_string()
                        )
                        if result:
                            raise smtplib.SMTPRecipientsRefused(result)
                else:
                    # TLS connection
                    with smtplib.SMTP(config['server'], config['port'], timeout=self.connection_timeout) as server:
                        server.starttls(context=context)
                        server.login(self.sender_email, self.sender_password)
                        result = server.sendmail(
                            from_addr=self.sender_email,
                            to_addrs=[recipient_email],
                            msg=email_content["message"].as_string()
                        )
                        if result:
                            raise smtplib.SMTPRecipientsRefused(result)
                        
            finally:
                socket.setdefaulttimeout(original_timeout)
        
        await asyncio.wait_for(
            loop.run_in_executor(None, send_sync),
            timeout=self.total_timeout
        )
    
    def _store_successful_email(self, user_id: str, email: str, processing_time: float):
        """Store successful email delivery record"""
        try:
            record = {
                "user_id": user_id,
                "email": email,
                "status": "delivered",
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "service": "render_network_email"
            }
            
            records_file = "email_delivery_log.json"
            records = []
            
            if os.path.exists(records_file):
                try:
                    with open(records_file, 'r') as f:
                        records = json.load(f)
                except:
                    records = []
            
            records.append(record)
            
            # Keep last 100 records
            if len(records) > 100:
                records = records[-100:]
            
            with open(records_file, 'w') as f:
                json.dump(records, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Failed to store delivery record: {e}")
    
    def _store_failed_email_attempt(self, user_id: str, email: str, error_msg: str):
        """Store failed email attempt"""
        try:
            record = {
                "user_id": user_id,
                "email": email,
                "status": "failed",
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
                "service": "render_network_email"
            }
            
            records_file = "email_delivery_log.json"
            records = []
            
            if os.path.exists(records_file):
                try:
                    with open(records_file, 'r') as f:
                        records = json.load(f)
                except:
                    records = []
            
            records.append(record)
            
            # Keep last 100 records
            if len(records) > 100:
                records = records[-100:]
            
            with open(records_file, 'w') as f:
                json.dump(records, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Failed to store failed attempt: {e}")
    
    def _prepare_email_content(self, prediction_data: Dict, patient_data: Dict, recipient_email: str) -> Dict:
        """Prepare email content"""
        prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
        confidence = round(prediction_data.get('confidence', 0) * 100, 1)
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏥 MediCare+ Insurance Report - {prediction_amount}"
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['To'] = recipient_email
        msg['Reply-To'] = self.sender_email
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>MediCare+ Report</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px;">
                    <h1 style="margin: 0; font-size: 24px;">🏥 MediCare+ Medical Insurance Report</h1>
                    <p style="margin: 5px 0 0 0;">AI-Powered Insurance Analysis</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <div style="font-size: 28px; font-weight: bold;">{prediction_amount}</div>
                    <div>Confidence: {confidence}% | {timestamp}</div>
                </div>
                
                <div style="margin-bottom: 25px;">
                    <h2 style="color: #667eea;">📋 Patient Details</h2>
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
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                    <p><strong>MediCare+ Platform</strong> | {timestamp}</p>
                    <p>Report sent to: {recipient_email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        return {"message": msg, "recipient": recipient_email}
    
    def format_currency(self, value: float) -> str:
        """Format currency in Indian Rupees"""
        return f"₹{value:,.0f}"

# Create global instance
render_network_email_service = RenderNetworkEmailService()

# Test function
async def test_render_network_email():
    """Test the render network email service"""
    print("🧪 TESTING RENDER NETWORK EMAIL SERVICE")
    print("="*80)
    
    # Test network connectivity
    network_result = render_network_email_service.test_network_connectivity()
    print(f"Network Test: {'✅ PASS' if network_result['success'] else '❌ FAIL'}")
    
    if not network_result['success']:
        print(f"Network Error: {network_result['message']}")
        return
    
    # Test Gmail connection
    connection_result = render_network_email_service.test_gmail_connection()
    print(f"Gmail Test: {'✅ PASS' if connection_result['success'] else '❌ FAIL'}")
    
    if not connection_result['success']:
        print(f"Gmail Error: {connection_result['message']}")
        return
    
    # Test email sending
    test_email = "gowthaamankrishna1998@gmail.com"
    test_prediction = {"prediction": 25000, "confidence": 0.88}
    test_patient_data = {
        "age": 28, "bmi": 24.5, "gender": "Male", "smoker": "No",
        "region": "South", "premium_annual_inr": 22000
    }
    
    result = await render_network_email_service.send_prediction_email(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data,
        user_id="test_user_123"
    )
    
    print(f"Email Test: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")

if __name__ == "__main__":
    asyncio.run(test_render_network_email())
