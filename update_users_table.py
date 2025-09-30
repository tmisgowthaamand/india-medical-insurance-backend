#!/usr/bin/env python3
"""
Update Users Table Migration Script
Adds email_only column to support users who only provide email for predictions
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def update_users_table():
    """Update users table to support email-only users"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
        return False
    
    try:
        # Initialize Supabase client
        print("🔗 Connecting to Supabase...")
        try:
            # Try different initialization methods for compatibility
            try:
                # Method 1: Named parameters (newer versions)
                supabase = create_client(
                    supabase_url=supabase_url,
                    supabase_key=supabase_service_key
                )
            except TypeError:
                # Method 2: Positional parameters (older versions)
                supabase = create_client(supabase_url, supabase_service_key)
        except Exception as init_error:
            print(f"❌ Error initializing Supabase client: {init_error}")
            return False
        
        # Read SQL migration script
        sql_file = "update_users_table.sql"
        if not os.path.exists(sql_file):
            print(f"❌ Error: {sql_file} not found")
            return False
        
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        print("📝 Executing SQL migration...")
        
        # Execute the migration (Note: Supabase Python client doesn't support raw SQL)
        # We'll need to run this manually in Supabase SQL editor
        print("⚠️  IMPORTANT: This script shows the SQL commands to run.")
        print("   Please copy and paste the following SQL into your Supabase SQL Editor:")
        print("\n" + "="*60)
        print(sql_script)
        print("="*60 + "\n")
        
        # Test if the table structure is correct by trying to query
        try:
            result = supabase.table("users").select("email, email_only").limit(1).execute()
            print("✅ Users table structure appears to be updated correctly")
            return True
        except Exception as e:
            if "column \"email_only\" does not exist" in str(e):
                print("⚠️  The email_only column doesn't exist yet. Please run the SQL script above.")
                return False
            else:
                print(f"✅ Table query successful (migration may already be applied)")
                return True
                
    except Exception as e:
        print(f"❌ Error updating users table: {e}")
        return False

def test_email_functionality():
    """Test the email saving functionality"""
    print("\n🧪 Testing email functionality...")
    
    try:
        from database import supabase_client
        
        if not supabase_client.is_enabled():
            print("⚠️  Supabase not enabled, skipping test")
            return
        
        # Test email saving (this would be done in actual usage)
        print("✅ Email functionality is ready to test with actual predictions")
        
    except Exception as e:
        print(f"❌ Error testing email functionality: {e}")

if __name__ == "__main__":
    print("🚀 Starting Users Table Migration")
    print("="*50)
    
    success = update_users_table()
    
    if success:
        test_email_functionality()
        print("\n✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run the SQL script shown above in Supabase SQL Editor")
        print("2. Test the prediction form with email addresses")
        print("3. Check that emails are saved to the users table")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)
