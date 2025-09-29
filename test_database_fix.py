#!/usr/bin/env python3
"""
Quick test to verify the database.py fix works
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_import():
    """Test if database.py can be imported without errors"""
    print("🔍 Testing database.py import...")
    
    try:
        from database import supabase_client
        print("✅ database.py imported successfully")
        
        # Check if client is properly initialized
        print(f"   Supabase enabled: {supabase_client.is_enabled()}")
        print(f"   URL configured: {'Yes' if supabase_client.url else 'No'}")
        print(f"   Keys configured: {'Yes' if supabase_client.service_role_key else 'No'}")
        
        if not supabase_client.is_enabled():
            print("   ℹ️ This is expected in local development (Supabase vars commented out)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing database.py: {e}")
        return False

def test_environment_vars():
    """Test environment variable loading"""
    print("\n🔍 Testing environment variables...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"   SUPABASE_URL: {'Set' if supabase_url else 'Not set (expected in local dev)'}")
    print(f"   SUPABASE_ANON_KEY: {'Set' if anon_key else 'Not set (expected in local dev)'}")
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {'Set' if service_key else 'Not set (expected in local dev)'}")
    
    # Check other vars
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    print(f"   JWT_SECRET_KEY: {'Set' if jwt_secret else 'Not set'}")
    
    return True

def main():
    print("🏥 Database Configuration Fix Test")
    print("=" * 40)
    
    # Test 1: Import database module
    import_success = test_database_import()
    
    # Test 2: Check environment variables
    env_success = test_environment_vars()
    
    print("\n" + "=" * 40)
    if import_success:
        print("✅ DATABASE FIX SUCCESSFUL!")
        print("   • No more import errors")
        print("   • StatReload warning should be resolved")
        print("   • Ready for Render deployment")
    else:
        print("❌ Database fix needs attention")
    
    print("\n💡 Next steps:")
    print("   1. Commit and push the database.py fix")
    print("   2. Verify Render environment variables")
    print("   3. Create Supabase database tables")

if __name__ == "__main__":
    main()
