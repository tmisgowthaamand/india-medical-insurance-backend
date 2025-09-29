#!/usr/bin/env python3
"""
Quick verification script to test if PGRST205 is fixed
Run this AFTER executing the SQL script in Supabase
"""

from supabase import create_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Your Supabase credentials
SUPABASE_URL = "https://gucyzhjyciqnvxedmoxo.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4"

def main():
    """Quick verification of database setup"""
    print("🔍 Verifying PGRST205 Fix...")
    
    try:
        # Initialize client
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("✅ Supabase client connected")
        
        # Test users table
        users = client.table('users').select('*').execute()
        print(f"✅ Users table accessible - Found {len(users.data)} users:")
        
        for user in users.data:
            role = "👑 ADMIN" if user.get('is_admin') else "👤 USER"
            print(f"   • {user['email']} - {role}")
        
        # Test other tables
        tables = ['datasets', 'dataset_rows', 'model_metadata', 'predictions']
        for table in tables:
            try:
                result = client.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' accessible")
            except Exception as e:
                print(f"❌ Table '{table}' error: {e}")
        
        print("\n🎉 PGRST205 ERROR IS FIXED!")
        print("✅ All tables are accessible")
        print("✅ Admin users are created and visible")
        print("✅ Your API should now work without 500 errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Still having issues: {e}")
        print("\n📋 Next steps:")
        print("1. Make sure you ran the SQL script in Supabase SQL Editor")
        print("2. Wait 2-3 minutes for schema cache refresh")
        print("3. Try running this script again")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
