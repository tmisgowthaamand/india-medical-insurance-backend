#!/usr/bin/env python3
"""
Complete Login/Signup Fix for MediCare+ Platform
Provides clear error messages for authentication issues
"""

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import re
from datetime import datetime
from fix_auth_error_messages import AuthErrorMessageFix

class LoginSignupFix:
    def __init__(self):
        self.auth_fix = AuthErrorMessageFix()
    
    async def improved_login(self, form_data: OAuth2PasswordRequestForm, supabase_client, load_users, save_users, create_access_token):
        """Improved login with better error messages"""
        print(f"Login attempt for: {form_data.username}")
        
        # Validate email format first
        email_validation = self.auth_fix.validate_email_format(form_data.username)
        if not email_validation["valid"]:
            raise HTTPException(status_code=400, detail=email_validation["message"])
        
        # Validate password
        if not form_data.password or len(form_data.password.strip()) == 0:
            raise HTTPException(status_code=400, detail="❌ Please enter your password")
        
        # Try Supabase first
        if supabase_client.is_enabled():
            try:
                user = await supabase_client.get_user(form_data.username)
                if user and user['password'] == form_data.password:
                    token = create_access_token({"sub": form_data.username, "is_admin": user.get("is_admin", False)})
                    return {
                        "access_token": token, 
                        "token_type": "bearer",
                        "email": form_data.username,
                        "is_admin": user.get("is_admin", False)
                    }
                elif user:
                    print(f"Password mismatch for user: {form_data.username}")
                    raise HTTPException(status_code=401, detail=f"❌ Incorrect password for '{form_data.username}'. Please try again.")
                else:
                    print(f"User not found in Supabase: {form_data.username}")
                    # Fall through to JSON fallback
            except HTTPException:
                raise
            except Exception as e:
                print(f"Supabase login error: {e}")
                raise HTTPException(status_code=500, detail="❌ Server error occurred. Please try again in a few minutes.")
        
        # Fallback to JSON file
        users = await load_users()
        
        if not users:
            # Create default users if none exist
            default_users = {
                "admin@example.com": {
                    "password": "admin123",
                    "created_at": datetime.now().isoformat(),
                    "is_admin": True
                },
                "user@example.com": {
                    "password": "user123",
                    "created_at": datetime.now().isoformat(),
                    "is_admin": False
                },
                "demo@example.com": {
                    "password": "demo123",
                    "created_at": datetime.now().isoformat(),
                    "is_admin": False
                }
            }
            await save_users(default_users)
            users = default_users
        
        # Try to find user by email
        user = users.get(form_data.username)
        if not user:
            print(f"User not found: {form_data.username}")
            print(f"Available users: {list(users.keys())}")
            raise HTTPException(status_code=401, detail=f"❌ No account found with email '{form_data.username}'. Please sign up first.")
        
        print(f"User found: {form_data.username}")
        
        # Check password
        password_valid = (form_data.password == user['password'])
        
        if not password_valid:
            print(f"Password mismatch for user: {form_data.username}")
            raise HTTPException(status_code=401, detail=f"❌ Incorrect password for '{form_data.username}'. Please try again.")
        
        token = create_access_token({"sub": form_data.username, "is_admin": user.get("is_admin", False)})
        return {
            "access_token": token, 
            "token_type": "bearer",
            "email": form_data.username,
            "is_admin": user.get("is_admin", False)
        }
    
    async def improved_signup(self, payload, supabase_client, load_users, save_users):
        """Improved signup with better error messages"""
        print(f"Signup attempt - Email: {payload.email}, Password length: {len(payload.password)}")
        
        # Validate email format
        email_validation = self.auth_fix.validate_email_format(payload.email)
        if not email_validation["valid"]:
            raise HTTPException(status_code=400, detail=email_validation["message"])
        
        # Validate password strength
        password_validation = self.auth_fix.validate_password_strength(payload.password)
        if not password_validation["valid"]:
            raise HTTPException(status_code=400, detail=password_validation["message"])
        
        # Try Supabase first
        if supabase_client.is_enabled():
            try:
                # Check if user already exists
                existing_user = await supabase_client.get_user(payload.email)
                if existing_user:
                    raise HTTPException(status_code=400, detail=f"❌ An account with '{payload.email}' already exists. Please login instead.")
                
                # Create user in Supabase
                is_admin = payload.email == "admin@example.com"
                result = await supabase_client.create_user(payload.email, payload.password, is_admin)
                
                if "error" in result:
                    raise HTTPException(status_code=500, detail=f"❌ Unable to create account: {result['error']}")
                
                return {"message": "✅ Account created successfully! Welcome to MediCare+", "email": payload.email}
            except HTTPException:
                raise
            except Exception as e:
                print(f"Supabase signup error: {e}")
                raise HTTPException(status_code=500, detail="❌ Unable to create account. Please try again in a few minutes.")
        
        # Fallback to JSON file
        users = await load_users()
        
        if payload.email in users:
            raise HTTPException(status_code=400, detail=f"❌ An account with '{payload.email}' already exists. Please login instead.")
        
        # Create user
        users[payload.email] = {
            "password": payload.password[:72],  # Store plain text for demo
            "created_at": datetime.now().isoformat(),
            "is_admin": payload.email == "admin@example.com"
        }
        
        await save_users(users)
        return {"message": "✅ Account created successfully! Welcome to MediCare+", "email": payload.email}

# Example usage and test cases
def demonstrate_error_messages():
    """Demonstrate the improved error messages"""
    auth_fix = AuthErrorMessageFix()
    
    print("="*70)
    print("🔧 IMPROVED AUTH ERROR MESSAGES - MediCare+ Platform")
    print("="*70)
    
    print("\n📧 EMAIL VALIDATION ERRORS:")
    print("-" * 40)
    
    # Test invalid email formats
    invalid_emails = ["", "invalid", "invalid@", "@gmail.com", "user..name@gmail.com"]
    for email in invalid_emails:
        result = auth_fix.validate_email_format(email)
        if not result["valid"]:
            print(f"'{email}' → {result['message']}")
    
    print("\n🔒 PASSWORD VALIDATION ERRORS:")
    print("-" * 40)
    
    # Test invalid passwords
    invalid_passwords = ["", "123", "a" * 130]
    for password in invalid_passwords:
        result = auth_fix.validate_password_strength(password)
        if not result["valid"]:
            print(f"'{password[:10]}...' → {result['message']}")
    
    print("\n🔐 LOGIN ERROR MESSAGES:")
    print("-" * 40)
    print(auth_fix.get_login_error_message("user_not_found", "newuser@gmail.com"))
    print(auth_fix.get_login_error_message("wrong_password", "user@gmail.com"))
    print(auth_fix.get_login_error_message("network_error"))
    
    print("\n📝 SIGNUP ERROR MESSAGES:")
    print("-" * 40)
    print(auth_fix.get_signup_error_message("email_exists", "existing@gmail.com"))
    print(auth_fix.get_signup_error_message("invalid_email"))
    print(auth_fix.get_signup_error_message("weak_password"))
    
    print("\n✅ SUCCESS MESSAGES:")
    print("-" * 40)
    print("✅ Login successful! Welcome back to MediCare+")
    print("✅ Account created successfully! Welcome to MediCare+")
    
    print("\n💡 WHAT USERS WILL SEE:")
    print("-" * 40)
    print("• Clear, specific error messages")
    print("• No generic 'Invalid credentials' messages")
    print("• Helpful suggestions for fixing issues")
    print("• Positive, encouraging success messages")

if __name__ == "__main__":
    demonstrate_error_messages()
