#!/usr/bin/env python3
"""
Create admin user in Supabase database
"""

import asyncio
import os
from dotenv import load_dotenv
from database import supabase_client

async def create_admin_user():
    """Create admin user in Supabase"""
    
    load_dotenv()
    
    print("🔧 Creating Admin User in Supabase")
    print("=" * 50)
    
    if not supabase_client.is_enabled():
        print("❌ Supabase is not enabled")
        return False
    
    # Admin user details
    admin_email = "admin@example.com"
    admin_password = "admin123"
    
    try:
        # Check if admin user already exists
        existing_user = await supabase_client.get_user(admin_email)
        
        if existing_user:
            print(f"✅ Admin user already exists: {admin_email}")
            print(f"   Is Admin: {existing_user.get('is_admin', False)}")
            
            # Update to ensure admin privileges
            if not existing_user.get('is_admin', False):
                print("🔄 Updating user to admin privileges...")
                # Note: You might need to update this manually in Supabase dashboard
                print("💡 Please update is_admin=true in Supabase dashboard for this user")
            
            return True
        else:
            print(f"🔄 Creating new admin user: {admin_email}")
            
            # Create admin user
            result = await supabase_client.create_user(admin_email, admin_password, is_admin=True)
            
            if "error" not in result:
                print(f"✅ Admin user created successfully!")
                print(f"   Email: {admin_email}")
                print(f"   Password: {admin_password}")
                print(f"   Is Admin: True")
                return True
            else:
                print(f"❌ Failed to create admin user: {result['error']}")
                return False
                
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

async def test_admin_login():
    """Test admin login"""
    
    print("\n🧪 Testing Admin Login")
    print("=" * 30)
    
    import requests
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    credentials_to_test = [
        ("admin@example.com", "admin123"),
        ("user@example.com", "user123")
    ]
    
    for email, password in credentials_to_test:
        print(f"\n🔑 Testing: {email}")
        
        try:
            login_data = {
                'username': email,
                'password': password
            }
            
            response = requests.post(
                f"{base_url}/login",
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Login successful!")
                print(f"      Email: {result.get('email')}")
                print(f"      Is Admin: {result.get('is_admin')}")
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                try:
                    error = response.json()
                    print(f"      Error: {error.get('message', 'Unknown error')}")
                except:
                    print(f"      Response: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def main():
    """Main function"""
    
    success = await create_admin_user()
    
    if success:
        await test_admin_login()
        
        print("\n" + "=" * 50)
        print("🎉 Admin user setup complete!")
        print("\n📋 Available Login Credentials:")
        print("   👑 Admin: admin@example.com / admin123")
        print("   👤 User:  user@example.com / user123")
        print("\n✅ You can now login with either account!")
    else:
        print("\n❌ Admin user setup failed")
        print("💡 You can still use: user@example.com / user123")

if __name__ == "__main__":
    asyncio.run(main())
