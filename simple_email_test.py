#!/usr/bin/env python3
"""
Simple Email Test - Send a basic email to check Gmail delivery
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from datetime import datetime

def send_simple_test_email():
    """Send a simple test email"""
    load_dotenv()
    
    sender_email = os.getenv("GMAIL_EMAIL")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient_email = "gokrishna98@gmail.com"
    
    print("📧 Sending simple test email...")
    print(f"From: {sender_email}")
    print(f"To: {recipient_email}")
    
    try:
        # Create simple email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"🏥 MediCare+ Simple Test - {datetime.now().strftime('%H:%M:%S')}"
        
        # Simple text body
        body = f"""
Hello!

This is a simple test email from MediCare+ Platform.

✅ If you receive this email, the Gmail integration is working correctly!

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
From: MediCare+ Email Service

Best regards,
MediCare+ Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print("✅ Simple test email sent successfully!")
        print("📬 Check your Gmail inbox (including spam folder)")
        print("📧 Subject: " + msg['Subject'])
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send simple test email: {e}")
        return False

if __name__ == "__main__":
    send_simple_test_email()
