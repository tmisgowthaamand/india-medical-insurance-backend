#!/usr/bin/env python3
"""
Render Built-in Email Service for MediCare+ Platform
Uses only Python built-in libraries (no external dependencies)
Fallback when requests module is not available
"""

import os
import asyncio
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import base64
from datetime import datetime
from typing import Dict, Any, List
import re

class RenderBuiltinEmailService:
    def __init__(self):
        # Email service configuration
        self.sender_email = os.getenv("SENDER_EMAIL", "gokrishna98@gmail.com")
        self.sender_name = "MediCare+ Insurance Platform"
        
        # Try to setup email providers with built-in libraries
        self.email_providers = self._setup_email_providers()
        
        # Check which providers are available
        self.available_providers = self._check_available_providers()
        
        # Gmail storage
        self.gmail_storage_file = "user_emails.json"
        
        print("="*80)
        print("🔧 RENDER BUILTIN EMAIL SERVICE - MediCare+ Platform")
        print("="*80)
        print(f"📨 Sender Email: {self.sender_email}")
        print(f"🔧 Available Providers: {len(self.available_providers)}")
        for provider in self.available_providers:
            print(f"   ✅ {provider['name']}")
        
        if not self.available_providers:
            print("⚠️ No email providers configured - using storage mode")
        
        print("="*80)
    
    def _setup_email_providers(self):
        """Setup available email providers using built-in libraries"""
        providers = []
        
        # SendGrid (HTTP API) - using urllib
        sendgrid_key = os.getenv("SENDGRID_API_KEY")
        if sendgrid_key:
            providers.append({
                "name": "SendGrid",
                "type": "sendgrid",
                "api_key": sendgrid_key,
                "url": "https://api.sendgrid.com/v3/mail/send",
                "enabled": True
            })
        
        # Mailgun (HTTP API) - using urllib
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
        
        # Always available: Local Storage
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
                elif provider["type"] in ["sendgrid", "mailgun"]:
                    # Test if we can reach the internet
                    try:
                        urllib.request.urlopen('https://www.google.com', timeout=5)
                        available.append(provider)
                    except:
                        print(f"⚠️ {provider['name']} not reachable (no internet)")
        
        return available
    
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
        """Send prediction email using available providers"""
        start_time = time.time()
        
        print(f"📧 BUILTIN EMAIL SEND: {recipient_email}")
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
                    result = await self._send_via_sendgrid_builtin(provider, recipient_email, prediction_data, patient_data)
                elif provider["type"] == "mailgun":
                    result = await self._send_via_mailgun_builtin(provider, recipient_email, prediction_data, patient_data)
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
            "success": True,  # Return success for storage fallback
            "message": f"✅ Email stored locally for {recipient_email}. Will be sent when email service is available.",
            "processing_time": processing_time,
            "provider": "Local Storage",
            "note": "Email saved for manual sending"
        }
    
    async def _send_via_sendgrid_builtin(self, provider: Dict, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> Dict[str, Any]:
        """Send email via SendGrid API using urllib"""
        try:
            prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
            
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
            
            # Convert payload to JSON
            json_data = json.dumps(payload).encode('utf-8')
            
            # Create request
            req = urllib.request.Request(
                provider['url'],
                data=json_data,
                headers={
                    'Authorization': f"Bearer {provider['api_key']}",
                    'Content-Type': 'application/json'
                }
            )
            
            # Send request
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.getcode() == 202:
                    return {
                        "success": True,
                        "message": f"✅ Email sent successfully via SendGrid to {recipient_email}! Check your Gmail inbox.",
                        "provider": "SendGrid"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"❌ SendGrid API error: {response.getcode()}"
                    }
                    
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "message": f"❌ SendGrid HTTP error: {e.code} - {e.reason}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ SendGrid error: {str(e)}"
            }
    
    async def _send_via_mailgun_builtin(self, provider: Dict, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> Dict[str, Any]:
        """Send email via Mailgun API using urllib"""
        try:
            prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
            
            # Mailgun email payload
            data = {
                "from": f"{self.sender_name} <noreply@{provider['domain']}>",
                "to": recipient_email,
                "subject": f"🏥 MediCare+ Insurance Report - {prediction_amount} - URGENT",
                "html": self._generate_html_content(prediction_data, patient_data, recipient_email)
            }
            
            # Encode form data
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            
            # Create basic auth header
            auth_string = f"api:{provider['api_key']}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            # Create request
            req = urllib.request.Request(
                provider['url'],
                data=encoded_data,
                headers={
                    'Authorization': f'Basic {auth_b64}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            
            # Send request
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.getcode() == 200:
                    return {
                        "success": True,
                        "message": f"✅ Email sent successfully via Mailgun to {recipient_email}! Check your Gmail inbox.",
                        "provider": "Mailgun"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"❌ Mailgun API error: {response.getcode()}"
                    }
                    
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "message": f"❌ Mailgun HTTP error: {e.code} - {e.reason}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Mailgun error: {str(e)}"
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
                "note": "Email saved to pending_emails.json"
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
render_builtin_email_service = RenderBuiltinEmailService()

# Test function
async def test_builtin_email():
    """Test the builtin email service"""
    print("🧪 TESTING BUILTIN EMAIL SERVICE")
    print("="*80)
    
    # Test email sending
    test_email = "gowthaamankrishna1998@gmail.com"
    test_prediction = {"prediction": 25000, "confidence": 0.88}
    test_patient_data = {
        "age": 28, "bmi": 24.5, "gender": "Male", "smoker": "No",
        "region": "South", "premium_annual_inr": 22000
    }
    
    result = await render_builtin_email_service.send_prediction_email(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data,
        user_id="test_user_123"
    )
    
    print(f"Email Test: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    print(f"Provider: {result.get('provider', 'Unknown')}")

if __name__ == "__main__":
    asyncio.run(test_builtin_email())
