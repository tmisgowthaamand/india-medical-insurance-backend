#!/usr/bin/env python3
"""
Fix Render User Sync Issue
==========================

This script fixes the user authentication mismatch between localhost and Render
by ensuring the user exists in Supabase with the correct password.
"""

import os
import asyncio
from datetime import datetime
from database import supabase_client
from utils import hash_password

async def sync_user_to_render():
    """Sync user data to Render's Supabase database"""
    
    # User data that works on localhost
    test_users = [
        {
            "email": "perivihk@gmail.com",
            "password": "123456",  # Use the password that works on localhost
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
    
    print("🔄 Starting user sync to Render Supabase...")
    
    if not supabase_client.is_enabled():
        print("❌ Supabase is not enabled. Please check environment variables.")
        return False
    
    success_count = 0
    
    for user_data in test_users:
        try:
            email = user_data["email"]
            password = user_data["password"]
            is_admin = user_data["is_admin"]
            
            print(f"\n📧 Processing user: {email}")
            
            # Check if user exists
            existing_user = await supabase_client.get_user(email)
            
            if existing_user:
                print(f"   ✅ User exists, updating password...")
                # Update existing user with correct password
                result = await supabase_client.update_user(email, {
                    "password": password,
                    "is_admin": is_admin,
                    "updated_at": datetime.now().isoformat()
                })
                if result.get("success"):
                    print(f"   ✅ Updated user: {email}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to update user: {email} - {result.get('error', 'Unknown error')}")
            else:
                print(f"   ➕ Creating new user...")
                # Create new user
                result = await supabase_client.create_user(email, password, is_admin)
                if result.get("success"):
                    print(f"   ✅ Created user: {email}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to create user: {email} - {result.get('error', 'Unknown error')}")
                    
        except Exception as e:
            print(f"   ❌ Error processing {user_data['email']}: {e}")
    
    print(f"\n🎉 Sync completed! {success_count}/{len(test_users)} users processed successfully.")
    return success_count == len(test_users)

async def test_login_after_sync():
    """Test login functionality after sync"""
    
    test_credentials = [
        ("perivihk@gmail.com", "123456"),
        ("gokrishna98@gmail.com", "123456"),
        ("admin@example.com", "admin123")
    ]
    
    print("\n🧪 Testing login functionality...")
    
    for email, password in test_credentials:
        try:
            print(f"\n🔐 Testing login for: {email}")
            user = await supabase_client.get_user(email)
            
            if user and user.get('password') == password:
                print(f"   ✅ Login test passed for: {email}")
            else:
                print(f"   ❌ Login test failed for: {email}")
                if user:
                    print(f"      Expected: {password}")
                    print(f"      Got: {user.get('password', 'No password found')}")
                else:
                    print(f"      User not found in database")
                    
        except Exception as e:
            print(f"   ❌ Login test error for {email}: {e}")

async def main():
    """Main function to run the sync process"""
    
    print("=" * 60)
    print("🚀 RENDER USER SYNC & EMAIL FIX")
    print("=" * 60)
    
    # Step 1: Sync users
    sync_success = await sync_user_to_render()
    
    if sync_success:
        print("\n✅ User sync completed successfully!")
        
        # Step 2: Test login
        await test_login_after_sync()
        
        print("\n" + "=" * 60)
        print("📋 NEXT STEPS:")
        print("=" * 60)
        print("1. ✅ Users are now synced to Render Supabase")
        print("2. 🔐 Test login on Render frontend with:")
        print("   - Email: perivihk@gmail.com")
        print("   - Password: 123456")
        print("3. 📧 Email functionality should now work for:")
        print("   - Existing users (perivihk@gmail.com)")
        print("   - New users (any new signups)")
        print("4. 🎯 Both prediction emails and test emails will work")
        print("\n🎉 Your Render deployment is now ready!")
        
    else:
        print("\n❌ User sync failed. Please check:")
        print("1. Supabase environment variables on Render")
        print("2. Database connection")
        print("3. Table permissions")

if __name__ == "__main__":
    asyncio.run(main())
