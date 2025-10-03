#!/usr/bin/env python3
"""
Optimized Email Service for MediCare+ Platform - Render Deployment
Handles sending prediction reports via Gmail SMTP with timeout optimization
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

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_EMAIL")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD")
        self.sender_name = "MediCare+ Platform"
        self.email_enabled = bool(self.sender_email and self.sender_password)
        
        # Timeout settings optimized for Render
        self.connection_timeout = 15  # 15 seconds for connection
        self.send_timeout = 30        # 30 seconds for sending
        self.total_timeout = 45       # 45 seconds total (well under 90s frontend timeout)
        
        if not self.email_enabled:
            print("⚠️ Email service disabled - Gmail credentials not configured")
            print("💡 Set GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables to enable email")
        else:
            print(f"✅ Email service enabled - Sender: {self.sender_email}")
            print(f"⏱️ Timeout settings: Connection={self.connection_timeout}s, Send={self.send_timeout}s, Total={self.total_timeout}s")
    
    def is_email_enabled(self) -> bool:
        """Check if email service is properly configured"""
        return self.email_enabled
        
    def create_prediction_email_template(self) -> str:
        """Create HTML email template for prediction reports"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediCare+ Prediction Report</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }
        .header h1 { margin: 0; font-size: 24px; }
        .header p { margin: 5px 0 0 0; opacity: 0.9; }
        .section { margin-bottom: 25px; }
        .section h2 { color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px; margin-bottom: 15px; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .info-item { background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea; }
        .info-item strong { color: #333; display: block; margin-bottom: 5px; }
        .prediction-highlight { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }
        .prediction-highlight .amount { font-size: 28px; font-weight: bold; margin-bottom: 5px; }
        .prediction-highlight .confidence { opacity: 0.9; }
        .risk-assessment { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .risk-high { background: #f8d7da; border-color: #f5c6cb; }
        .risk-low { background: #d4edda; border-color: #c3e6cb; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }
        .disclaimer { background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #666; }
        @media (max-width: 600px) { .info-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 MediCare+ Medical Insurance Report</h1>
            <p>Professional AI-Powered Insurance Claim Analysis</p>
            <p style="font-size: 12px; opacity: 0.8;">This is an official report from MediCare+ Platform</p>
        </div>
        
        <div class="section">
            <h2>📋 Patient Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Age</strong>
                    {{ patient_data.age }} years
                </div>
                <div class="info-item">
                    <strong>BMI</strong>
                    {{ patient_data.bmi }}
                </div>
                <div class="info-item">
                    <strong>Gender</strong>
                    {{ patient_data.gender }}
                </div>
                <div class="info-item">
                    <strong>Smoking Status</strong>
                    {{ patient_data.smoker }}
                </div>
                <div class="info-item">
                    <strong>Region</strong>
                    {{ patient_data.region }}
                </div>
                <div class="info-item">
                    <strong>Annual Premium</strong>
                    ₹{{ patient_data.premium_annual_inr or 'Estimated' }}
                </div>
            </div>
        </div>
        
        <div class="prediction-highlight">
            <div class="amount">{{ prediction_amount }}</div>
            <div class="confidence">Confidence: {{ confidence }}% | Generated: {{ timestamp }}</div>
        </div>
        
        <div class="section">
            <h2>🎯 BMI Analysis</h2>
            <div class="info-item">
                <strong>BMI Category</strong>
                {{ bmi_category }}
            </div>
            <div class="risk-assessment {{ risk_class }}">
                <strong>Health Risk Level: {{ risk_level }}</strong>
                <p>{{ risk_description }}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Key Insights</h2>
            <ul>
                {% for insight in insights %}
                <li>{{ insight }}</li>
                {% endfor %}
            </ul>
        </div>
        
        <div class="disclaimer">
            <strong>⚠️ Medical Disclaimer:</strong> This AI-generated prediction is for educational and informational purposes only. 
            It should not be used as a substitute for professional medical advice, diagnosis, or treatment. 
            Always consult with qualified healthcare providers for medical decisions.
        </div>
        
        <div class="footer">
            <p><strong>MediCare+ AI Platform</strong> | © 2024 MediCare+ Healthcare Technology</p>
            <p>Powered by Advanced Machine Learning & Medical Data Analytics</p>
            <p>Report generated on {{ timestamp }} for {{ recipient_email }}</p>
            <p style="margin-top: 10px; font-size: 10px; color: #999;">
                If you received this email by mistake, please contact us at {{ sender_email }}<br>
                This email was sent from an automated system. Please do not reply directly to this email.
            </p>
        </div>
    </div>
</body>
</html>
        """
    
    def format_currency(self, value: float) -> str:
        """Format currency in Indian Rupees"""
        return f"₹{value:,.0f}"
    
    def generate_insights(self, patient_data: Dict, prediction: Dict) -> list:
        """Generate key insights based on patient data and prediction"""
        insights = []
        
        age = int(patient_data.get('age', 0))
        bmi = float(patient_data.get('bmi', 0))
        smoker = patient_data.get('smoker', '')
        
        if age > 50:
            insights.append(f"Age factor: At {age} years, age-related health risks may contribute to higher claim probability")
        
        if bmi < 18.5:
            insights.append("BMI indicates underweight status - consider nutritional consultation")
        elif bmi > 30:
            insights.append("BMI indicates obesity - lifestyle modifications recommended to reduce health risks")
        elif 18.5 <= bmi <= 25:
            insights.append("BMI is in healthy range - maintain current lifestyle for optimal health")
        
        if smoker == 'Yes':
            insights.append("Smoking significantly increases health risks and claim probability - cessation programs recommended")
        else:
            insights.append("Non-smoking status contributes positively to health profile")
        
        confidence = prediction.get('confidence', 0)
        if confidence > 0.8:
            insights.append("High prediction confidence indicates reliable estimate based on comprehensive data analysis")
        elif confidence < 0.6:
            insights.append("Moderate prediction confidence - additional health data may improve accuracy")
        
        return insights
    
    async def send_prediction_email_async(self, recipient_email: str, prediction_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async email sending with timeout control for Render deployment"""
        
        try:
            # Set socket timeout for the entire operation
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.total_timeout)
            
            print(f"📧 Starting async email send to {recipient_email} (timeout: {self.total_timeout}s)")
            
            # Check if email service is enabled
            if not self.is_email_enabled():
                print("⚠️ Email service is disabled - storing locally")
                success = await self._store_email_report_locally_async(recipient_email, prediction_data, patient_data)
                return {
                    "success": False,
                    "message": f"Email service is not configured. Gmail credentials (GMAIL_EMAIL and GMAIL_APP_PASSWORD) are required to send emails.",
                    "mock": True,
                    "demo_mode": True
                }
            
            # Prepare email data quickly
            prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
            confidence = round(prediction_data.get('confidence', 0) * 100, 1)
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
            
            # BMI analysis (simplified for speed)
            bmi = float(patient_data.get('bmi', 0))
            if bmi < 18.5:
                bmi_category, risk_level, risk_class = "Underweight", "Moderate", "risk-assessment"
                risk_description = "BMI below normal range may indicate nutritional deficiencies"
            elif bmi < 25:
                bmi_category, risk_level, risk_class = "Normal Weight", "Low", "risk-low"
                risk_description = "BMI in healthy range - optimal for insurance risk assessment"
            elif bmi < 30:
                bmi_category, risk_level, risk_class = "Overweight", "Moderate", "risk-assessment"
                risk_description = "BMI above normal range - lifestyle modifications recommended"
            else:
                bmi_category, risk_level, risk_class = "Obese", "High", "risk-high"
                risk_description = "BMI indicates obesity - significant health risks and higher claim probability"
            
            # Generate insights quickly
            insights = self.generate_insights(patient_data, prediction_data)
            
            # Create lightweight email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🏥 MediCare+ Report - {prediction_amount}"
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['X-Mailer'] = "MediCare+ v1.0"
            
            # Create HTML content
            template = Template(self.create_prediction_email_template())
            html_content = template.render(
                patient_data=patient_data,
                prediction_amount=prediction_amount,
                confidence=confidence,
                timestamp=timestamp,
                bmi_category=bmi_category,
                risk_level=risk_level,
                risk_class=risk_class,
                risk_description=risk_description,
                insights=insights,
                recipient_email=recipient_email,
                sender_email=self.sender_email
            )
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email with strict timeout control
            print(f"🔗 Connecting to {self.smtp_server}:{self.smtp_port} (timeout: {self.connection_timeout}s)")
            
            # Use executor for timeout control
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._send_email_sync_optimized, msg, recipient_email)
                try:
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: future.result()), 
                        timeout=self.total_timeout
                    )
                    
                    print(f"✅ Email sent successfully to {recipient_email}")
                    return {
                        "success": True,
                        "message": f"Prediction report sent successfully to {recipient_email}! Check your inbox.",
                        "send_time": result.get("send_time", "unknown")
                    }
                    
                except asyncio.TimeoutError:
                    print(f"⏱️ Email send timeout after {self.total_timeout}s - storing locally")
                    future.cancel()
                    success = await self._store_email_report_locally_async(recipient_email, prediction_data, patient_data)
                    return {
                        "success": False,
                        "message": f"Email sending timed out after {self.total_timeout} seconds. Please try again or check your internet connection.",
                        "timeout": True
                    }
            
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}")
            success = await self._store_email_report_locally_async(recipient_email, prediction_data, patient_data)
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}. Please check your email address and try again.",
                "error": str(e)
            }
        finally:
            # Restore original timeout
            socket.setdefaulttimeout(original_timeout)
    
    def _send_email_sync_optimized(self, msg, recipient_email: str) -> Dict[str, Any]:
        """Optimized synchronous email sending with timeout control"""
        start_time = datetime.now()
        
        try:
            # Create optimized SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Use timeout on socket level
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout) as server:
                print("🔐 Starting TLS...")
                server.starttls(context=context)
                print("🔑 Logging in...")
                server.login(self.sender_email, self.sender_password)
                print("📧 Sending email...")
                
                server.sendmail(
                    from_addr=self.sender_email,
                    to_addrs=[recipient_email],
                    msg=msg.as_string()
                )
            
            send_time = (datetime.now() - start_time).total_seconds()
            print(f"⏱️ Email sent in {send_time:.2f} seconds")
            
            return {"success": True, "send_time": f"{send_time:.2f}s"}
            
        except Exception as e:
            send_time = (datetime.now() - start_time).total_seconds()
            print(f"❌ Email send failed after {send_time:.2f}s: {e}")
            raise e
    
    async def _store_email_report_locally_async(self, recipient_email: str, prediction_data: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Async version of local storage"""
        try:
            report = {
                "recipient": recipient_email,
                "prediction": prediction_data,
                "patient_data": patient_data,
                "timestamp": datetime.now().isoformat(),
                "status": "stored_locally"
            }
            
            # Use async file operations
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, self._store_report_sync, report)
            
            if success:
                print(f"✅ Email report stored locally for {recipient_email}")
            return success
            
        except Exception as e:
            print(f"❌ Failed to store email report locally: {e}")
            return False
    
    def _store_report_sync(self, report: Dict) -> bool:
        """Synchronous report storage"""
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
    
    def _simulate_email_send(self, recipient_email: str, prediction_data: Dict, patient_data: Dict):
        """Simulate email sending for demo purposes"""
        prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
        confidence = round(prediction_data.get('confidence', 0) * 100, 1)
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
        
        print("="*60)
        print("📧 DEMO EMAIL SIMULATION")
        print("="*60)
        print(f"To: {recipient_email}")
        print(f"From: MediCare+ Platform <{self.sender_email}>")
        print(f"Subject: 🏥 MediCare+ Prediction Report - {prediction_amount}")
        print(f"Generated: {timestamp}")
        print("-"*60)
        print("📋 PATIENT INFORMATION:")
        print(f"   Age: {patient_data.get('age')} years")
        print(f"   BMI: {patient_data.get('bmi')}")
        print(f"   Gender: {patient_data.get('gender')}")
        print(f"   Smoker: {patient_data.get('smoker')}")
        print(f"   Region: {patient_data.get('region')}")
        print(f"   Premium: ₹{patient_data.get('premium_annual_inr', 'Estimated')}")
        print("-"*60)
        print("🎯 PREDICTION RESULTS:")
        print(f"   Predicted Claim: {prediction_amount}")
        print(f"   Confidence: {confidence}%")
        print("-"*60)
        print("✅ Email simulation completed successfully!")
        print("💡 To send real emails, configure actual Gmail credentials")
        print("="*60)
    
    def send_prediction_email(self, recipient_email: str, prediction_data: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Send prediction report via email with graceful error handling and fallback"""
        
        # Always try to store report locally first as backup
        local_backup_success = self._store_email_report_locally(recipient_email, prediction_data, patient_data)
        
        # Check if email service is enabled
        if not self.is_email_enabled():
            print("⚠️ Email service is disabled - report stored locally instead")
            return local_backup_success
        
        print(f"📧 Attempting to send email to {recipient_email}...")
        
        try:
            # Prepare email data
            prediction_amount = self.format_currency(prediction_data.get('prediction', 0))
            confidence = round(prediction_data.get('confidence', 0) * 100, 1)
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
            
            # BMI analysis
            bmi = float(patient_data.get('bmi', 0))
            if bmi < 18.5:
                bmi_category = "Underweight"
                risk_level = "Moderate"
                risk_class = "risk-assessment"
                risk_description = "BMI below normal range may indicate nutritional deficiencies"
            elif bmi < 25:
                bmi_category = "Normal Weight"
                risk_level = "Low"
                risk_class = "risk-low"
                risk_description = "BMI in healthy range - optimal for insurance risk assessment"
            elif bmi < 30:
                bmi_category = "Overweight"
                risk_level = "Moderate"
                risk_class = "risk-assessment"
                risk_description = "BMI above normal range - lifestyle modifications recommended"
            else:
                bmi_category = "Obese"
                risk_level = "High"
                risk_class = "risk-high"
                risk_description = "BMI indicates obesity - significant health risks and higher claim probability"
            
            # Generate insights
            insights = self.generate_insights(patient_data, prediction_data)
            
            # Create email with enhanced headers for better Gmail delivery
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🏥 MediCare+ Medical Insurance Prediction Report - {prediction_amount}"
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Reply-To'] = self.sender_email
            msg['X-Mailer'] = "MediCare+ Platform v1.0"
            msg['X-Priority'] = "3"  # Normal priority
            msg['Message-ID'] = f"<{datetime.now().strftime('%Y%m%d%H%M%S')}.{recipient_email.replace('@', '_at_').replace('.', '_dot_')}@medicare-plus.com>"
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0530')
            msg['MIME-Version'] = "1.0"
            msg['Content-Type'] = "multipart/alternative"
            # Remove bulk headers that might trigger spam filters
            # msg['List-Unsubscribe'] = f"<mailto:{self.sender_email}?subject=Unsubscribe>"
            # msg['X-Auto-Response-Suppress'] = "OOF, DR, RN, NRN, AutoReply"
            # msg['Precedence'] = "bulk"
            
            # Create HTML content
            template = Template(self.create_prediction_email_template())
            html_content = template.render(
                patient_data=patient_data,
                prediction_amount=prediction_amount,
                confidence=confidence,
                timestamp=timestamp,
                bmi_category=bmi_category,
                risk_level=risk_level,
                risk_class=risk_class,
                risk_description=risk_description,
                insights=insights,
                recipient_email=recipient_email,
                sender_email=self.sender_email
            )
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email with optimized connection
            print(f"🔗 Connecting to {self.smtp_server}:{self.smtp_port}...")
            context = ssl.create_default_context()
            
            # Optimize SSL context for speed
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                print("🔐 Starting TLS...")
                server.starttls(context=context)
                print("🔑 Logging in...")
                server.login(self.sender_email, self.sender_password)
                print("📧 Sending email...")
                
                # Send with proper envelope
                server.sendmail(
                    from_addr=self.sender_email,
                    to_addrs=[recipient_email],
                    msg=msg.as_string()
                )
            
            print(f"✅ Email sent successfully to {recipient_email}")
            print(f"📬 Subject: {msg['Subject']}")
            print(f"⏰ Sent at: {timestamp}")
            
            # Skip database storage for faster email sending
            print(f"📧 Email sent successfully - skipping database storage for speed")
            
            return True
            
        except (OSError, ConnectionError, TimeoutError) as e:
            print(f"⚠️ Network error: {e}")
            print("📝 Email report already stored locally as backup")
            return local_backup_success  # Return success since we have local backup
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication failed: {e}")
            print("💡 Check Gmail App Password configuration")
            print("📝 Email report already stored locally as backup")
            return local_backup_success  # Return success since we have local backup
        except smtplib.SMTPRecipientsRefused as e:
            print(f"❌ Recipient email refused: {e}")
            print("💡 Check recipient email address")
            print("📝 Email report already stored locally as backup")
            return local_backup_success  # Return success since we have local backup
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error: {e}")
            print("📝 Email report already stored locally as backup")
            return local_backup_success  # Return success since we have local backup
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}")
            print(f"📝 Email report already stored locally as backup")
            return local_backup_success  # Return success since we have local backup
    
    def _store_email_report_locally(self, recipient_email: str, prediction_data: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Store email report locally when sending fails"""
        try:
            report = {
                "recipient": recipient_email,
                "prediction": prediction_data,
                "patient_data": patient_data,
                "timestamp": datetime.now().isoformat(),
                "status": "stored_locally"
            }
            
            # Store in local file
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
            
            print(f"✅ Email report stored locally for {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store email report locally: {e}")
            return False

# Global email service instance
email_service = EmailService()
