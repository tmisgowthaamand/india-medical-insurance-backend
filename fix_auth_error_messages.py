#!/usr/bin/env python3
"""
Fix Authentication Error Messages for MediCare+ Platform
Provides clear, user-friendly error messages for login/signup issues
"""

import re
import smtplib
import ssl
from typing import Dict, Any

class AuthErrorMessageFix:
    def __init__(self):
        print("🔧 AUTH ERROR MESSAGE FIX - MediCare+ Platform")
        print("="*60)
    
    def validate_email_format(self, email: str) -> Dict[str, Any]:
        """Validate email format and provide specific error messages"""
        if not email or email.strip() == "":
            return {
                "valid": False,
                "error": "Email address is required",
                "message": "❌ Please enter your email address"
            }
        
        email = email.strip().lower()
        
        # Check basic email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {
                "valid": False,
                "error": "Invalid email format",
                "message": "❌ Please enter a valid email address (e.g., user@gmail.com)"
            }
        
        # Check for common email issues
        if email.count('@') != 1:
            return {
                "valid": False,
                "error": "Invalid email format",
                "message": "❌ Email address must contain exactly one @ symbol"
            }
        
        local_part, domain = email.split('@')
        
        if len(local_part) == 0:
            return {
                "valid": False,
                "error": "Invalid email format",
                "message": "❌ Email address cannot start with @"
            }
        
        if len(domain) == 0 or '.' not in domain:
            return {
                "valid": False,
                "error": "Invalid email format",
                "message": "❌ Please enter a valid domain (e.g., gmail.com)"
            }
        
        # Check for suspicious patterns
        if '..' in email:
            return {
                "valid": False,
                "error": "Invalid email format",
                "message": "❌ Email address cannot contain consecutive dots"
            }
        
        return {
            "valid": True,
            "email": email,
            "message": "✅ Valid email format"
        }
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength and provide specific feedback"""
        if not password:
            return {
                "valid": False,
                "error": "Password is required",
                "message": "❌ Please enter a password"
            }
        
        if len(password) < 6:
            return {
                "valid": False,
                "error": "Password too short",
                "message": "❌ Password must be at least 6 characters long"
            }
        
        if len(password) > 128:
            return {
                "valid": False,
                "error": "Password too long",
                "message": "❌ Password must be less than 128 characters"
            }
        
        # Check for basic security
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        if not has_letter and not has_number:
            return {
                "valid": False,
                "error": "Password too weak",
                "message": "❌ Password must contain at least letters or numbers"
            }
        
        return {
            "valid": True,
            "message": "✅ Password meets requirements"
        }
    
    def get_login_error_message(self, error_type: str, email: str = "") -> str:
        """Get user-friendly login error messages"""
        error_messages = {
            "invalid_credentials": f"❌ Wrong email or password. Please check your credentials and try again.",
            "user_not_found": f"❌ No account found with email '{email}'. Please sign up first.",
            "wrong_password": f"❌ Incorrect password for '{email}'. Please try again.",
            "account_locked": f"❌ Account temporarily locked due to multiple failed attempts. Try again later.",
            "email_not_verified": f"❌ Please verify your email address before logging in.",
            "server_error": f"❌ Server error occurred. Please try again in a few minutes.",
            "network_error": f"❌ Cannot connect to server. Please check your internet connection.",
            "invalid_email_format": f"❌ Please enter a valid email address."
        }
        
        return error_messages.get(error_type, f"❌ Login failed. Please try again.")
    
    def get_signup_error_message(self, error_type: str, email: str = "") -> str:
        """Get user-friendly signup error messages"""
        error_messages = {
            "email_exists": f"❌ An account with '{email}' already exists. Please login instead.",
            "invalid_email": f"❌ Please enter a valid email address (e.g., user@gmail.com).",
            "weak_password": f"❌ Password must be at least 6 characters with letters and numbers.",
            "password_mismatch": f"❌ Passwords do not match. Please re-enter your password.",
            "server_error": f"❌ Unable to create account. Please try again in a few minutes.",
            "network_error": f"❌ Cannot connect to server. Please check your internet connection.",
            "missing_fields": f"❌ Please fill in all required fields (email and password)."
        }
        
        return error_messages.get(error_type, f"❌ Signup failed. Please try again.")
    
    def get_gmail_error_message(self, smtp_error: str) -> str:
        """Convert SMTP errors to user-friendly messages"""
        error_lower = smtp_error.lower()
        
        if "authentication" in error_lower or "username" in error_lower or "password" in error_lower:
            return "❌ Gmail authentication failed. Please check your email and app password."
        
        if "recipient" in error_lower or "refused" in error_lower:
            return "❌ The recipient email address was rejected. Please check the email address."
        
        if "timeout" in error_lower or "timed out" in error_lower:
            return "❌ Email sending timed out. Please check your internet connection and try again."
        
        if "connection" in error_lower or "connect" in error_lower:
            return "❌ Cannot connect to Gmail servers. Please check your internet connection."
        
        if "ssl" in error_lower or "tls" in error_lower:
            return "❌ Secure connection failed. Please try again."
        
        return f"❌ Email sending failed: {smtp_error}"

def create_improved_auth_responses():
    """Create improved authentication response templates"""
    
    auth_fix = AuthErrorMessageFix()
    
    print("\n📋 IMPROVED ERROR MESSAGES:")
    print("-" * 50)
    
    # Login error examples
    print("🔐 LOGIN ERRORS:")
    print(auth_fix.get_login_error_message("wrong_password", "user@gmail.com"))
    print(auth_fix.get_login_error_message("user_not_found", "newuser@gmail.com"))
    print(auth_fix.get_login_error_message("invalid_credentials"))
    print(auth_fix.get_login_error_message("network_error"))
    
    print("\n📝 SIGNUP ERRORS:")
    print(auth_fix.get_signup_error_message("email_exists", "existing@gmail.com"))
    print(auth_fix.get_signup_error_message("invalid_email"))
    print(auth_fix.get_signup_error_message("weak_password"))
    print(auth_fix.get_signup_error_message("password_mismatch"))
    
    print("\n📧 EMAIL ERRORS:")
    print(auth_fix.get_gmail_error_message("Authentication failed"))
    print(auth_fix.get_gmail_error_message("Recipient refused"))
    print(auth_fix.get_gmail_error_message("Connection timeout"))
    
    print("\n✅ SUCCESS MESSAGES:")
    print("✅ Login successful! Welcome back to MediCare+")
    print("✅ Account created successfully! Welcome to MediCare+")
    print("✅ Email sent successfully! Check your inbox.")
    
    return auth_fix

if __name__ == "__main__":
    create_improved_auth_responses()
