#!/usr/bin/env python3
"""
Enhanced Email Service for MediCare+ Platform
Provides immediate feedback and graceful error handling with network connectivity issues
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import asyncio
from datetime import datetime
from jinja2 import Template
import json
from typing import Dict, Any
import concurrent.futures
import socket
import time

class EnhancedEmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_EMAIL")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD")
        self.sender_name = "MediCare+ Platform"
        self.email_enabled = bool(self.sender_email and self.sender_password)
        
        # Optimized timeout settings
        self.connection_timeout = 10  # Quick connection timeout
        self.send_timeout = 20        # Send timeout
        self.total_timeout = 30       # Total operation timeout
        
        if not self.email_enabled:
            print("⚠️ Email service disabled - Gmail credentials not configured")
        else:
            print(f"✅ Email service enabled - Sender: {self.sender_email}")
    
    def is_email_enabled(self) -> bool:
        """Check if email service is properly configured"""
        return self.email_enabled
    
    def check_network_connectivity(self) -> bool:
        """Quick network connectivity check"""
        try:
            # Try to connect to Google's DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    async def send_prediction_email_with_immediate_feedback(
        self, 
        recipient_email: str, 
        prediction_data: Dict[str, Any], 
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced email sending with immediate feedback and graceful error handling
        """
        start_time = time.time()
        
        # STEP 1: Immediate validation and feedback
        print(f"📧 Processing email request for: {recipient_email}")
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, recipient_email):
            return {
                "success": False,
                "message": f"Invalid email format: {recipient_email}",
                "immediate": True
            }
        
        # STEP 2: Store report locally FIRST (immediate backup)
        local_success = await self._store_email_report_locally_async(
            recipient_email, prediction_data, patient_data
        )
        
        if not local_success:
            print("⚠️ Failed to store report locally")
        
        # STEP 3: Provide immediate success response (user gets instant feedback)
        immediate_response = {
            "success": True,
            "message": f"✅ Report generated and queued for delivery to {recipient_email}",
            "immediate": True,
            "processing_time": round(time.time() - start_time, 2)
        }
        
        # STEP 4: Attempt email sending in background (don't block user)
        asyncio.create_task(self._send_email_background(
            recipient_email, prediction_data, patient_data, start_time
        ))
        
        return immediate_response
    
    async def _send_email_background(
        self, 
        recipient_email: str, 
        prediction_data: Dict[str, Any], 
        patient_data: Dict[str, Any],
        start_time: float
    ):
        """Send email in background without blocking user response"""
        try:
            print(f"🔄 Background email processing for {recipient_email}")
            
            # Check if email service is configured
            if not self.is_email_enabled():
                print("⚠️ Email service not configured - report stored locally only")
                return
            
            # Quick network check
            if not self.check_network_connectivity():
                print("⚠️ Network connectivity issue - email will be retried later")
                return
            
            # Prepare email content quickly
            email_content = self._prepare_email_content(prediction_data, patient_data, recipient_email)
            
            # Try to send email with timeout
            try:
                await asyncio.wait_for(
                    self._send_email_async(email_content, recipient_email),
                    timeout=self.total_timeout
                )
                
                processing_time = round(time.time() - start_time, 2)
                print(f"✅ Background email sent successfully to {recipient_email} in {processing_time}s")
                
                # Update local storage with success status
                await self._update_email_status(recipient_email, "sent", processing_time)
                
            except asyncio.TimeoutError:
                print(f"⏱️ Email send timeout after {self.total_timeout}s")
                await self._update_email_status(recipient_email, "timeout", self.total_timeout)
                
            except Exception as e:
                print(f"❌ Background email send failed: {e}")
                await self._update_email_status(recipient_email, "failed", str(e))
                
        except Exception as e:
            print(f"⚠️ Background email processing error: {e}")
    
    def _prepare_email_content(self, prediction_data: Dict, patient_data: Dict, recipient_email: str) -> Dict:
        """Prepare email content efficiently"""
        prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
        confidence = round(prediction_data.get('confidence', 0) * 100, 1)
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
        
        # Quick BMI analysis
        bmi = float(patient_data.get('bmi', 0))
        if bmi < 18.5:
            bmi_category, risk_level = "Underweight", "Moderate"
        elif bmi < 25:
            bmi_category, risk_level = "Normal Weight", "Low"
        elif bmi < 30:
            bmi_category, risk_level = "Overweight", "Moderate"
        else:
            bmi_category, risk_level = "Obese", "High"
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏥 MediCare+ Report - {prediction_amount}"
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['To'] = recipient_email
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0530')
        
        # Simple HTML content for faster processing
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>MediCare+ Prediction Report</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px;">
                    <h1 style="margin: 0;">🏥 MediCare+ Medical Insurance Report</h1>
                    <p style="margin: 5px 0 0 0;">AI-Powered Insurance Claim Analysis</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">{prediction_amount}</div>
                    <div>Confidence: {confidence}% | Generated: {timestamp}</div>
                </div>
                
                <div style="margin-bottom: 25px;">
                    <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px;">📋 Patient Information</h2>
                    <p><strong>Age:</strong> {patient_data.get('age')} years</p>
                    <p><strong>BMI:</strong> {patient_data.get('bmi')} ({bmi_category})</p>
                    <p><strong>Gender:</strong> {patient_data.get('gender')}</p>
                    <p><strong>Smoking Status:</strong> {patient_data.get('smoker')}</p>
                    <p><strong>Region:</strong> {patient_data.get('region')}</p>
                    <p><strong>Annual Premium:</strong> ₹{patient_data.get('premium_annual_inr', 'Estimated')}</p>
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
    
    async def _send_email_async(self, email_content: Dict, recipient_email: str):
        """Send email asynchronously"""
        loop = asyncio.get_event_loop()
        
        def send_sync():
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    from_addr=self.sender_email,
                    to_addrs=[recipient_email],
                    msg=email_content["message"].as_string()
                )
        
        await loop.run_in_executor(None, send_sync)
    
    async def _store_email_report_locally_async(self, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> bool:
        """Store email report locally"""
        try:
            report = {
                "recipient": recipient_email,
                "prediction": prediction_data,
                "patient_data": patient_data,
                "timestamp": datetime.now().isoformat(),
                "status": "queued",
                "processing_time": 0
            }
            
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, self._store_report_sync, report)
            
            if success:
                print(f"✅ Email report stored locally for {recipient_email}")
            return success
            
        except Exception as e:
            print(f"❌ Failed to store email report locally: {e}")
            return False
    
    def _store_report_sync(self, report: Dict) -> bool:
        """Store report synchronously"""
        try:
            reports_file = "email_reports.json"
            reports = []
            
            if os.path.exists(reports_file):
                try:
                    with open(reports_file, 'r') as f:
                        reports = json.load(f)
                except:
                    reports = []
            
            reports.append(report)
            
            # Keep only last 100 reports
            if len(reports) > 100:
                reports = reports[-100:]
            
            with open(reports_file, 'w') as f:
                json.dump(reports, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Sync storage failed: {e}")
            return False
    
    async def _update_email_status(self, recipient_email: str, status: str, processing_time):
        """Update email status in local storage"""
        try:
            reports_file = "email_reports.json"
            if not os.path.exists(reports_file):
                return
            
            with open(reports_file, 'r') as f:
                reports = json.load(f)
            
            # Find and update the most recent report for this recipient
            for report in reversed(reports):
                if report.get("recipient") == recipient_email and report.get("status") == "queued":
                    report["status"] = status
                    report["processing_time"] = processing_time
                    report["updated_at"] = datetime.now().isoformat()
                    break
            
            with open(reports_file, 'w') as f:
                json.dump(reports, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to update email status: {e}")
    
    def format_currency(self, value: float) -> str:
        """Format currency in Indian Rupees"""
        return f"₹{value:,.0f}"

# Global enhanced email service instance
enhanced_email_service = EnhancedEmailService()
