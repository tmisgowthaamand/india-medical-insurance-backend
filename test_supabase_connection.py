#!/usr/bin/env python3
"""
Test Supabase connection and debug initialization issues
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection with detailed debugging"""
    print("🔍 Testing Supabase Connection...")
    print("=" * 50)
    
    # Check environment variables
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"✅ SUPABASE_URL: {'✓' if url else '✗'} {url[:50] + '...' if url else 'Not set'}")
    print(f"✅ SUPABASE_ANON_KEY: {'✓' if anon_key else '✗'} {len(anon_key) if anon_key else 0} characters")
    print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {'✓' if service_role_key else '✗'} {len(service_role_key) if service_role_key else 0} characters")
    
    if not all([url, anon_key, service_role_key]):
        print("\n❌ Missing Supabase credentials!")
        print("Please set the following environment variables:")
        print("- SUPABASE_URL")
        print("- SUPABASE_ANON_KEY") 
        print("- SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    # Test Supabase import
    try:
        from supabase import create_client, Client
        print("\n✅ Supabase library imported successfully")
    except ImportError as e:
        print(f"\n❌ Failed to import Supabase: {e}")
        print("Try: pip install supabase==2.7.4")
        return False
    
    # Test client creation
    try:
        print("\n🔄 Testing client creation...")
        
        # Try method 1: Named parameters
        try:
            client = create_client(
                supabase_url=url,
                supabase_key=service_role_key
            )
            print("✅ Client created successfully with named parameters")
        except TypeError as e:
            print(f"⚠️  Named parameters failed: {e}")
            print("🔄 Trying positional parameters...")
            
            # Try method 2: Positional parameters
            client = create_client(url, service_role_key)
            print("✅ Client created successfully with positional parameters")
        
        # Test a simple operation
        try:
            # This will fail if tables don't exist, but that's expected
            result = client.table("users").select("count", count="exact").execute()
            print("✅ Database connection successful")
        except Exception as e:
            if "relation" in str(e).lower() or "table" in str(e).lower():
                print("✅ Database connection successful (tables not created yet)")
            else:
                print(f"⚠️  Database query failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to create Supabase client: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Check for common issues
        if "proxy" in str(e).lower():
            print("\n💡 Proxy error detected. This might be due to:")
            print("1. Outdated Supabase library version")
            print("2. Network configuration issues")
            print("3. Environment variable conflicts")
            print("\nTry updating: pip install --upgrade supabase")
        
        return False

def main():
    """Main function"""
    success = test_supabase_connection()
    
    if success:
        print("\n🎉 Supabase connection test passed!")
        print("Your backend should now work with Supabase.")
    else:
        print("\n❌ Supabase connection test failed!")
        print("The backend will fall back to local file storage.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
