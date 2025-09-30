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
    
    def send_prediction_email(self, recipient_email: str, prediction_data: Dict, patient_data: Dict) -> bool:
        """Send prediction report via email"""
        try:
            if not self.sender_email or not self.sender_password:
                print("❌ Gmail credentials not configured")
                return False
            
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
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

# Global email service instance
email_service = EmailService()
