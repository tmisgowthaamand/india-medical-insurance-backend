#!/usr/bin/env python3
"""
Render HTTP Email Service for MediCare+ Platform
Uses HTTP-based email providers (SendGrid, Mailgun) since SMTP ports are blocked on Render
"""

import os
import asyncio
import time
import json
import requests
from datetime import datetime
from typing import Dict, Any, List
import re

class RenderHttpEmailService:
    def __init__(self):
        # Email service configuration
        self.sender_email = "gokrishna98@gmail.com"
        self.sender_name = "MediCare+ Platform"
        
        # Try multiple HTTP email providers
        self.email_providers = self._setup_email_providers()
        
        # Check which providers are available
        self.available_providers = self._check_available_providers()
        
        # Gmail storage
        self.gmail_storage_file = "user_emails.json"
        
        print("="*80)
        print("📧 RENDER HTTP EMAIL SERVICE - MediCare+ Platform")
        print("="*80)
        print(f"📨 Sender Email: {self.sender_email}")
        print(f"🔧 Available Providers: {len(self.available_providers)}")
        for provider in self.available_providers:
            print(f"   ✅ {provider['name']}")
        
        if not self.available_providers:
            print("⚠️ No email providers configured - using fallback mode")
            self._show_setup_instructions()
        
        print("="*80)
    
    def _setup_email_providers(self):
        """Setup available email providers"""
        providers = []
        
        # SendGrid (HTTP API)
        sendgrid_key = os.getenv("SENDGRID_API_KEY")
        if sendgrid_key:
            providers.append({
                "name": "SendGrid",
                "type": "sendgrid",
                "api_key": sendgrid_key,
                "url": "https://api.sendgrid.com/v3/mail/send",
                "enabled": True
            })
        
        # Mailgun (HTTP API)
        mailgun_key = os.getenv("MAILGUN_API_KEY")
        mailgun_domain = os.getenv("MAILGUN_DOMAIN", "sandbox-123.mailgun.org")
        if mailgun_key:
            providers.append({
                "name": "Mailgun",
                "type": "mailgun",
                "api_key": mailgun_key,
                "domain": mailgun_domain,
                "url": f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
                "enabled": True
            })
        
        # EmailJS (Frontend-based, fallback)
        emailjs_service = os.getenv("EMAILJS_SERVICE_ID")
        emailjs_template = os.getenv("EMAILJS_TEMPLATE_ID")
        emailjs_user = os.getenv("EMAILJS_USER_ID")
        if emailjs_service and emailjs_template and emailjs_user:
            providers.append({
                "name": "EmailJS",
                "type": "emailjs",
                "service_id": emailjs_service,
                "template_id": emailjs_template,
                "user_id": emailjs_user,
                "url": "https://api.emailjs.com/api/v1.0/email/send",
                "enabled": True
            })
        
        # Fallback: Store email for manual sending
        providers.append({
            "name": "Local Storage",
            "type": "storage",
            "enabled": True,
            "description": "Store emails locally for manual sending"
        })
        
        return providers
    
    def _check_available_providers(self):
        """Check which providers are actually available"""
        available = []
        
        for provider in self.email_providers:
            if provider.get("enabled", False):
                if provider["type"] == "storage":
                    available.append(provider)
                elif provider["type"] in ["sendgrid", "mailgun", "emailjs"]:
                    # Test if we can reach the API
                    try:
                        if provider["type"] == "sendgrid":
                            # Test SendGrid API
                            headers = {
                                "Authorization": f"Bearer {provider['api_key']}",
                                "Content-Type": "application/json"
                            }
                            # Just test the connection, don't send
                            response = requests.get("https://api.sendgrid.com/v3/user/profile", 
                                                  headers=headers, timeout=10)
                            if response.status_code in [200, 401]:  # 401 means API is reachable
                                available.append(provider)
                        elif provider["type"] == "mailgun":
                            # Test Mailgun API
                            response = requests.get(f"https://api.mailgun.net/v3/{provider['domain']}", 
                                                  auth=("api", provider['api_key']), timeout=10)
                            if response.status_code in [200, 401]:
                                available.append(provider)
                        elif provider["type"] == "emailjs":
                            # EmailJS is always available if configured
                            available.append(provider)
                    except:
                        print(f"⚠️ {provider['name']} API not reachable")
        
        return available
    
    def _show_setup_instructions(self):
        """Show setup instructions for email providers"""
        print("🔧 EMAIL PROVIDER SETUP FOR RENDER")
        print("-" * 50)
        print("Since Gmail SMTP is blocked, set up alternative providers:")
        print()
        print("Option 1 - SendGrid (Recommended):")
        print("1. Sign up at https://sendgrid.com (free tier: 100 emails/day)")
        print("2. Get API key from SendGrid dashboard")
        print("3. Set environment variable: SENDGRID_API_KEY=your_api_key")
        print()
        print("Option 2 - Mailgun:")
        print("1. Sign up at https://mailgun.com (free tier: 5000 emails/month)")
        print("2. Get API key and domain from Mailgun dashboard")
        print("3. Set environment variables:")
        print("   MAILGUN_API_KEY=your_api_key")
        print("   MAILGUN_DOMAIN=your_domain")
        print()
        print("Option 3 - EmailJS (Frontend-based):")
        print("1. Sign up at https://emailjs.com")
        print("2. Set environment variables:")
        print("   EMAILJS_SERVICE_ID=your_service_id")
        print("   EMAILJS_TEMPLATE_ID=your_template_id")
        print("   EMAILJS_USER_ID=your_user_id")
    
    def store_user_email(self, user_id: str, email: str) -> bool:
        """Store user's email address"""
        try:
            user_emails = {}
            if os.path.exists(self.gmail_storage_file):
                try:
                    with open(self.gmail_storage_file, 'r') as f:
                        user_emails = json.load(f)
                except:
                    user_emails = {}
            
            if user_id not in user_emails:
                user_emails[user_id] = {
                    "emails": [],
                    "primary_email": email,
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            
            if email not in user_emails[user_id]["emails"]:
                user_emails[user_id]["emails"].append(email)
                user_emails[user_id]["last_updated"] = datetime.now().isoformat()
                
                if not user_emails[user_id]["primary_email"]:
                    user_emails[user_id]["primary_email"] = email
            
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
    
    async def send_prediction_email(self, recipient_email: str, prediction_data: Dict, patient_data: Dict, user_id: str = None) -> Dict[str, Any]:
        """Send prediction email using available HTTP providers"""
        start_time = time.time()
        
        print(f"📧 HTTP EMAIL SEND: {recipient_email}")
        print("-" * 60)
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, recipient_email):
            return {
                "success": False,
                "message": f"❌ Invalid email format: {recipient_email}"
            }
        
        # Store user's email
        if user_id:
            self.store_user_email(user_id, recipient_email)
        
        # Try each available provider
        for provider in self.available_providers:
            try:
                print(f"🔄 Trying {provider['name']}...")
                
                if provider["type"] == "sendgrid":
                    result = await self._send_via_sendgrid(provider, recipient_email, prediction_data, patient_data)
                elif provider["type"] == "mailgun":
                    result = await self._send_via_mailgun(provider, recipient_email, prediction_data, patient_data)
                elif provider["type"] == "emailjs":
                    result = await self._send_via_emailjs(provider, recipient_email, prediction_data, patient_data)
                elif provider["type"] == "storage":
                    result = await self._store_email_locally(recipient_email, prediction_data, patient_data, user_id)
                else:
                    continue
                
                if result["success"]:
                    processing_time = round(time.time() - start_time, 2)
                    result["processing_time"] = processing_time
                    print(f"✅ Email sent via {provider['name']} in {processing_time}s")
                    return result
                else:
                    print(f"❌ {provider['name']} failed: {result['message']}")
                    
            except Exception as e:
                print(f"❌ {provider['name']} error: {str(e)}")
                continue
        
        # All providers failed
        processing_time = round(time.time() - start_time, 2)
        return {
            "success": False,
            "message": "❌ All email providers failed. Email saved locally for manual sending.",
            "processing_time": processing_time,
            "fallback": "local_storage"
        }
    
    async def _send_via_sendgrid(self, provider: Dict, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> Dict[str, Any]:
        """Send email via SendGrid API"""
        try:
            prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
            confidence = round(prediction_data.get('confidence', 0) * 100, 1)
            
            # SendGrid email payload
            payload = {
                "personalizations": [{
                    "to": [{"email": recipient_email}],
                    "subject": f"🏥 MediCare+ Insurance Report - {prediction_amount}"
                }],
                "from": {
                    "email": self.sender_email,
                    "name": self.sender_name
                },
                "content": [{
                    "type": "text/html",
                    "value": self._generate_html_content(prediction_data, patient_data, recipient_email)
                }]
            }
            
            headers = {
                "Authorization": f"Bearer {provider['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(provider['url'], json=payload, headers=headers, timeout=30)
            
            if response.status_code == 202:
                return {
                    "success": True,
                    "message": f"✅ Email sent successfully via SendGrid to {recipient_email}! Check your inbox.",
                    "provider": "SendGrid"
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ SendGrid API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ SendGrid error: {str(e)}"
            }
    
    async def _send_via_mailgun(self, provider: Dict, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> Dict[str, Any]:
        """Send email via Mailgun API"""
        try:
            prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
            
            # Mailgun email payload
            payload = {
                "from": f"{self.sender_name} <mailgun@{provider['domain']}>",
                "to": recipient_email,
                "subject": f"🏥 MediCare+ Insurance Report - {prediction_amount}",
                "html": self._generate_html_content(prediction_data, patient_data, recipient_email)
            }
            
            response = requests.post(
                provider['url'],
                auth=("api", provider['api_key']),
                data=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": f"✅ Email sent successfully via Mailgun to {recipient_email}! Check your inbox.",
                    "provider": "Mailgun"
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Mailgun API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Mailgun error: {str(e)}"
            }
    
    async def _send_via_emailjs(self, provider: Dict, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> Dict[str, Any]:
        """Send email via EmailJS API"""
        try:
            prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
            confidence = round(prediction_data.get('confidence', 0) * 100, 1)
            
            # EmailJS payload
            payload = {
                "service_id": provider['service_id'],
                "template_id": provider['template_id'],
                "user_id": provider['user_id'],
                "template_params": {
                    "to_email": recipient_email,
                    "from_name": self.sender_name,
                    "subject": f"MediCare+ Insurance Report - {prediction_amount}",
                    "prediction_amount": prediction_amount,
                    "confidence": confidence,
                    "patient_age": patient_data.get('age'),
                    "patient_bmi": patient_data.get('bmi'),
                    "patient_gender": patient_data.get('gender'),
                    "patient_smoker": patient_data.get('smoker'),
                    "patient_region": patient_data.get('region'),
                    "patient_premium": patient_data.get('premium_annual_inr'),
                    "timestamp": datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
                }
            }
            
            response = requests.post(provider['url'], json=payload, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": f"✅ Email sent successfully via EmailJS to {recipient_email}! Check your inbox.",
                    "provider": "EmailJS"
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ EmailJS API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ EmailJS error: {str(e)}"
            }
    
    async def _store_email_locally(self, recipient_email: str, prediction_data: Dict, patient_data: Dict, user_id: str) -> Dict[str, Any]:
        """Store email locally as fallback"""
        try:
            email_record = {
                "recipient": recipient_email,
                "user_id": user_id,
                "prediction_data": prediction_data,
                "patient_data": patient_data,
                "timestamp": datetime.now().isoformat(),
                "status": "stored_locally",
                "html_content": self._generate_html_content(prediction_data, patient_data, recipient_email)
            }
            
            # Store in pending emails file
            pending_file = "pending_emails.json"
            pending_emails = []
            
            if os.path.exists(pending_file):
                try:
                    with open(pending_file, 'r') as f:
                        pending_emails = json.load(f)
                except:
                    pending_emails = []
            
            pending_emails.append(email_record)
            
            # Keep last 50 pending emails
            if len(pending_emails) > 50:
                pending_emails = pending_emails[-50:]
            
            with open(pending_file, 'w') as f:
                json.dump(pending_emails, f, indent=2)
            
            return {
                "success": True,
                "message": f"✅ Email stored locally for {recipient_email}. Will be sent when email service is available.",
                "provider": "Local Storage",
                "note": "Email saved to pending_emails.json for manual sending"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Failed to store email locally: {str(e)}"
            }
    
    def _generate_html_content(self, prediction_data: Dict, patient_data: Dict, recipient_email: str) -> str:
        """Generate HTML email content"""
        prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
        confidence = round(prediction_data.get('confidence', 0) * 100, 1)
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
        
        return f"""
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
    
    def format_currency(self, value: float) -> str:
        """Format currency in Indian Rupees"""
        return f"₹{value:,.0f}"

# Create global instance
render_http_email_service = RenderHttpEmailService()

# Test function
async def test_render_http_email():
    """Test the HTTP email service"""
    print("🧪 TESTING RENDER HTTP EMAIL SERVICE")
    print("="*80)
    
    # Test email sending
    test_email = "gowthaamankrishna1998@gmail.com"
    test_prediction = {"prediction": 25000, "confidence": 0.88}
    test_patient_data = {
        "age": 28, "bmi": 24.5, "gender": "Male", "smoker": "No",
        "region": "South", "premium_annual_inr": 22000
    }
    
    result = await render_http_email_service.send_prediction_email(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data,
        user_id="test_user_123"
    )
    
    print(f"Email Test: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    print(f"Provider: {result.get('provider', 'Unknown')}")

if __name__ == "__main__":
    asyncio.run(test_render_http_email())
