#!/usr/bin/env python3
"""
Test Gmail Email Sending
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

def test_gmail_connection():
    """Test Gmail SMTP connection and send a test email"""
    load_dotenv()
    
    sender_email = os.getenv("GMAIL_EMAIL")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print("🧪 Testing Gmail Email Configuration")
    print("="*50)
    print(f"📧 Sender Email: {sender_email}")
    print(f"🔑 App Password: {'✅ Set' if sender_password else '❌ Not set'}")
    print(f"🔑 Password Length: {len(sender_password) if sender_password else 0}")
    
    if not sender_email or not sender_password:
        print("❌ Gmail credentials not properly configured")
        return False
    
    try:
        # Create test email
        recipient_email = sender_email  # Send to self for testing
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "🏥 MediCare+ Email Test - " + str(os.getpid())
        
        body = """
        <html>
        <body>
        <h2>🏥 MediCare+ Email Test</h2>
        <p>This is a test email to verify Gmail SMTP configuration.</p>
        <p><strong>✅ If you receive this email, the configuration is working!</strong></p>
        <p>Sent from: MediCare+ Platform</p>
        <p>Time: """ + str(os.times()) + """</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        print("📤 Attempting to send test email...")
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("🔗 Connecting to Gmail SMTP...")
            server.starttls(context=context)
            print("🔐 Starting TLS...")
            
            print("🔑 Logging in...")
            server.login(sender_email, sender_password)
            print("✅ Login successful!")
            
            print("📧 Sending email...")
            server.send_message(msg)
            print("✅ Email sent successfully!")
        
        print(f"📬 Check your Gmail inbox: {recipient_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Check your Gmail App Password")
        print("💡 Make sure 2FA is enabled on your Google account")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_gmail_connection()
    if success:
        print("\n🎉 Email test completed successfully!")
        print("📧 Check your Gmail inbox for the test email")
    else:
        print("\n❌ Email test failed. Please check configuration.")
