#!/usr/bin/env python3
"""
Supabase Setup Verification Script
Run this after executing the SQL migration to verify everything works
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from database import supabase_client

# Load environment variables
load_dotenv()

async def verify_supabase_setup():
    """Verify that Supabase is properly configured and tables exist"""
    
    print("🏥 MediCare+ Supabase Verification")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in environment")
        return False
    else:
        print(f"✅ SUPABASE_URL: {supabase_url[:50]}...")
    
    if not supabase_service_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not found in environment")
        return False
    else:
        print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {supabase_service_key[:20]}...")
    
    if supabase_anon_key:
        print(f"✅ SUPABASE_ANON_KEY: {supabase_anon_key[:20]}...")
    else:
        print("⚠️ SUPABASE_ANON_KEY not found (optional)")
    
    # Check database client initialization
    print("\n2. Checking database client...")
    if not supabase_client.is_enabled():
        print("❌ Supabase client is not enabled")
        return False
    else:
        print("✅ Supabase client initialized successfully")
    
    # Test table access
    print("\n3. Testing table access...")
    tables_to_test = ["users", "datasets", "dataset_rows", "model_metadata", "predictions"]
    
    for table in tables_to_test:
        try:
            result = supabase_client.client.table(table).select("*").limit(1).execute()
            print(f"✅ Table '{table}' accessible")
        except Exception as e:
            print(f"❌ Table '{table}' error: {e}")
            return False
    
    # Test user operations
    print("\n4. Testing user operations...")
    try:
        # Check if admin user exists
        admin_user = await supabase_client.get_user("admin@medicare.com")
        if admin_user:
            print("✅ Default admin user found")
        else:
            print("⚠️ Default admin user not found")
        
        # Test creating a test user
        test_email = "test@verification.com"
        existing_test_user = await supabase_client.get_user(test_email)
        
        if not existing_test_user:
            result = await supabase_client.create_user(test_email, "test123", False)
            if "error" in result:
                print(f"❌ Error creating test user: {result['error']}")
                return False
            else:
                print("✅ Test user created successfully")
                
                # Clean up test user
                try:
                    supabase_client.client.table("users").delete().eq("email", test_email).execute()
                    print("✅ Test user cleaned up")
                except Exception as e:
                    print(f"⚠️ Could not clean up test user: {e}")
        else:
            print("✅ User operations working (test user already exists)")
    
    except Exception as e:
        print(f"❌ User operations error: {e}")
        return False
    
    # Test model metadata
    print("\n5. Testing model metadata...")
    try:
        model_metadata = await supabase_client.get_latest_model_metadata()
        if model_metadata:
            print("✅ Model metadata accessible")
        else:
            print("⚠️ No model metadata found (this is normal for new setup)")
    except Exception as e:
        print(f"❌ Model metadata error: {e}")
        return False
    
    print("\n🎉 All verifications passed!")
    print("\nNext steps:")
    print("1. Your backend should now work without PGRST205 errors")
    print("2. Test signup at: https://india-medical-insurance-backend.onrender.com/signup")
    print("3. Default admin login: admin@medicare.com / admin123")
    print("4. Your Vercel frontend should now work properly")
    
    return True

async def test_signup_endpoint():
    """Test the signup endpoint specifically"""
    print("\n6. Testing signup endpoint simulation...")
    try:
        test_email = "signup_test@verification.com"
        
        # Check if user already exists
        existing_user = await supabase_client.get_user(test_email)
        if existing_user:
            # Delete existing test user
            supabase_client.client.table("users").delete().eq("email", test_email).execute()
        
        # Create new user (simulating signup)
        result = await supabase_client.create_user(test_email, "signup123", False)
        
        if "error" in result:
            print(f"❌ Signup simulation failed: {result['error']}")
            return False
        else:
            print("✅ Signup endpoint simulation successful")
            
            # Verify user was created
            created_user = await supabase_client.get_user(test_email)
            if created_user:
                print("✅ User retrieval after signup works")
                
                # Clean up
                supabase_client.client.table("users").delete().eq("email", test_email).execute()
                print("✅ Test cleanup completed")
                return True
            else:
                print("❌ User not found after creation")
                return False
    
    except Exception as e:
        print(f"❌ Signup simulation error: {e}")
        return False

if __name__ == "__main__":
    async def main():
        success = await verify_supabase_setup()
        if success:
            signup_success = await test_signup_endpoint()
            if signup_success:
                print("\n✅ Complete verification successful!")
                print("Your PGRST205 error should now be resolved.")
                sys.exit(0)
            else:
                print("\n❌ Signup test failed")
                sys.exit(1)
        else:
            print("\n❌ Verification failed")
            print("\nTroubleshooting:")
            print("1. Make sure you ran the SQL migration in Supabase")
            print("2. Check your environment variables")
            print("3. Verify your Supabase project is active")
            sys.exit(1)
    
    asyncio.run(main())
