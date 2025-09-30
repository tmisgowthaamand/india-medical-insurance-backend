#!/usr/bin/env python3
"""
Test Email Storage Functionality
Tests if email addresses can be saved to the users table
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import supabase_client

async def test_email_storage():
    """Test email storage functionality"""
    print("🧪 Testing Email Storage Functionality")
    print("="*50)
    
    if not supabase_client.is_enabled():
        print("❌ Supabase is not enabled. Check environment variables:")
        print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL', 'Not set')}")
        print(f"   SUPABASE_SERVICE_ROLE_KEY: {'Set' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'Not set'}")
        return False
    
    print("✅ Supabase client is enabled")
    
    # Test email addresses
    test_emails = [
        "test.user@example.com",
        "patient@healthcare.com",
        "demo@medicare.com"
    ]
    
    for email in test_emails:
        print(f"\n📧 Testing email: {email}")
        try:
            result = await supabase_client.save_email_to_users(email)
            if result.get("success"):
                print(f"   ✅ Success: {result.get('message', 'Email saved')}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test retrieving users
    print(f"\n👥 Retrieving all users...")
    try:
        users = await supabase_client.get_all_users()
        print(f"   ✅ Found {len(users)} users in database")
        for user in users[-3:]:  # Show last 3 users
            email_only = user.get('email_only', False)
            user_type = "Email-only" if email_only else "Registered"
            print(f"   📧 {user['email']} ({user_type})")
    except Exception as e:
        print(f"   ❌ Error retrieving users: {e}")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_email_storage())
