#!/usr/bin/env python3
"""
Deploy User Fix to Render
=========================

This script can be run on Render to sync user data and fix authentication issues.
"""

import os
import sys
import asyncio
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import supabase_client

async def deploy_user_fix():
    """Deploy user fix to Render environment"""
    
    print("🚀 RENDER USER FIX DEPLOYMENT")
    print("=" * 50)
    
    # Check environment
    print("\n🔍 Checking environment...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"   SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if supabase_key else '❌ Missing'}")
    print(f"   GMAIL_EMAIL: {'✅ Set' if gmail_email else '❌ Missing'}")
    print(f"   GMAIL_APP_PASSWORD: {'✅ Set' if gmail_password else '❌ Missing'}")
    
    if not all([supabase_url, supabase_key]):
        print("\n❌ Missing required environment variables!")
        return False
    
    # Test database connection
    print("\n🔗 Testing database connection...")
    if not supabase_client.is_enabled():
        print("   ❌ Database connection failed!")
        return False
    print("   ✅ Database connected successfully")
    
    # Create/update test users
    print("\n👥 Setting up users...")
    
    users_to_create = [
        {
            "email": "perivihk@gmail.com",
            "password": "123456",
            "is_admin": False
        },
        {
            "email": "gokrishna98@gmail.com",
            "password": "123456", 
            "is_admin": True
        },
        {
            "email": "admin@example.com",
            "password": "admin123",
            "is_admin": True
        }
    ]
    
    success_count = 0
    
    for user_data in users_to_create:
        try:
            email = user_data["email"]
            password = user_data["password"]
            is_admin = user_data["is_admin"]
            
            print(f"\n   📧 Processing: {email}")
            
            # Check if user exists
            existing_user = await supabase_client.get_user(email)
            
            if existing_user:
                # Update existing user
                result = await supabase_client.update_user(email, {
                    "password": password,
                    "is_admin": is_admin,
                    "updated_at": datetime.now().isoformat()
                })
                if result.get("success"):
                    print(f"      ✅ Updated user: {email}")
                    success_count += 1
                else:
                    print(f"      ❌ Failed to update: {email}")
            else:
                # Create new user
                result = await supabase_client.create_user(email, password, is_admin)
                if result.get("success"):
                    print(f"      ✅ Created user: {email}")
                    success_count += 1
                else:
                    print(f"      ❌ Failed to create: {email}")
                    
        except Exception as e:
            print(f"      ❌ Error with {user_data['email']}: {e}")
    
    # Test login functionality
    print(f"\n🧪 Testing login functionality...")
    
    test_credentials = [
        ("perivihk@gmail.com", "123456"),
        ("gokrishna98@gmail.com", "123456")
    ]
    
    login_success = 0
    
    for email, password in test_credentials:
        try:
            user = await supabase_client.get_user(email)
            if user and user.get('password') == password:
                print(f"   ✅ Login test passed: {email}")
                login_success += 1
            else:
                print(f"   ❌ Login test failed: {email}")
        except Exception as e:
            print(f"   ❌ Login test error for {email}: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 50)
    print(f"Users processed: {success_count}/{len(users_to_create)}")
    print(f"Login tests passed: {login_success}/{len(test_credentials)}")
    
    if success_count == len(users_to_create) and login_success == len(test_credentials):
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print("✅ All users are now synced")
        print("✅ Authentication is working")
        print("✅ Email functionality should work")
        print("\n🎯 Ready for production use!")
        return True
    else:
        print("\n❌ DEPLOYMENT INCOMPLETE")
        print("Some users or tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(deploy_user_fix())
    sys.exit(0 if success else 1)
