#!/usr/bin/env python3
"""
Email Service for MediCare+ Platform
Handles sending prediction reports via Gmail SMTP
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from jinja2 import Template
import json
from typing import Dict, Any

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_EMAIL")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD")
        
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
            <h1>🏥 MediCare+ Prediction Report</h1>
            <p>AI-Powered Medical Insurance Analysis</p>
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
            <p>Generated by MediCare+ AI Platform | © 2024 MediCare+ | Powered by Advanced Machine Learning</p>
            <p>This report was generated on {{ timestamp }} for {{ recipient_email }}</p>
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
    
    def send_prediction_email(self, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> bool:
        """Send prediction report via email"""
        try:
            if not self.sender_email or not self.sender_password:
                print("❌ Gmail credentials not configured. Email functionality disabled.")
                print("💡 To enable email functionality:")
                print("   1. Set GMAIL_EMAIL=your-email@gmail.com in .env")
                print("   2. Set GMAIL_APP_PASSWORD=your-app-password in .env")
                print("   3. Generate App Password at: https://myaccount.google.com/apppasswords")
                return False
            
            # Check if app password is still placeholder
            if self.sender_password == "your-gmail-app-password-here" or "demo" in self.sender_password.lower():
                print(f"📧 SETUP REQUIRED: Gmail App Password not configured for {self.sender_email}")
                print("💡 To send real emails to Gmail inbox:")
                print("   1. Go to: https://myaccount.google.com/apppasswords")
                print("   2. Sign in with gokrishna98@gmail.com")
                print("   3. Generate app password for 'MediCare Platform'")
                print("   4. Replace 'your-gmail-app-password-here' in .env file")
                print("   5. Restart backend server")
                print("📋 Currently simulating email send...")
                # Simulate successful email sending for demo purposes
                self._simulate_email_send(recipient_email, prediction_data, patient_data)
                return True
            
            print(f"📧 REAL EMAIL MODE: Sending to {recipient_email} from {self.sender_email}")
            print(f"🔑 Using app password: {self.sender_password[:4]}...{self.sender_password[-4:]}")
            
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
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🏥 MediCare+ Prediction Report - {prediction_amount}"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
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
                recipient_email=recipient_email
            )
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            print(f"🔗 Connecting to {self.smtp_server}:{self.smtp_port}...")
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                print("🔐 Starting TLS...")
                server.starttls(context=context)
                print("🔑 Logging in...")
                server.login(self.sender_email, self.sender_password)
                print("📧 Sending email...")
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {recipient_email}")
            print(f"📬 Subject: {msg['Subject']}")
            print(f"⏰ Sent at: {timestamp}")
            
            # Store email report in database (async call handled in backend)
            try:
                import asyncio
                from database import supabase_client
                report_data = {
                    "prediction": prediction_data,
                    "patient_data": patient_data,
                    "email_content": {
                        "subject": msg['Subject'],
                        "prediction_amount": prediction_amount,
                        "confidence": confidence,
                        "timestamp": timestamp
                    }
                }
                # Run async function in event loop
                asyncio.create_task(supabase_client.store_email_report(recipient_email, report_data, "sent"))
            except Exception as db_error:
                print(f"⚠️ Failed to store email report in database: {db_error}")
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication failed: {e}")
            print("💡 Check Gmail App Password configuration")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            print(f"❌ Recipient email refused: {e}")
            print("💡 Check recipient email address")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return False

# Global email service instance
email_service = EmailService()
