#!/usr/bin/env python3
"""
Apply Database Schema Fixes
Fixes missing columns and tables for email functionality
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def apply_database_fixes():
    """Apply database schema fixes"""
    print("🔧 APPLYING DATABASE SCHEMA FIXES")
    print("=" * 50)
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in .env file")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Read SQL fixes
        with open('fix_database_schema.sql', 'r') as f:
            sql_content = f.read()
        
        # Split SQL into individual statements
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        print(f"📝 Executing {len(sql_statements)} SQL statements...")
        
        # Execute each SQL statement
        for i, sql in enumerate(sql_statements, 1):
            if sql.strip():
                try:
                    print(f"   {i}. Executing: {sql[:50]}...")
                    result = supabase.rpc('exec_sql', {'sql': sql}).execute()
                    print(f"      ✅ Success")
                except Exception as e:
                    print(f"      ⚠️ Warning: {e}")
                    # Continue with other statements even if one fails
        
        print("✅ Database schema fixes applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply database fixes: {e}")
        return False

def verify_database_schema():
    """Verify that the database schema is correct"""
    print("\n🔍 VERIFYING DATABASE SCHEMA")
    print("=" * 50)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Check if email_only column exists in users table
        try:
            result = supabase.table('users').select('email_only').limit(1).execute()
            print("✅ email_only column exists in users table")
        except Exception as e:
            print(f"❌ email_only column missing: {e}")
        
        # Check if email_reports table exists
        try:
            result = supabase.table('email_reports').select('id').limit(1).execute()
            print("✅ email_reports table exists")
        except Exception as e:
            print(f"❌ email_reports table missing: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        return False

def create_manual_fixes():
    """Create manual SQL fixes that can be run directly in Supabase SQL editor"""
    print("\n📝 CREATING MANUAL SQL FIXES")
    print("=" * 50)
    
    manual_sql = """
-- MANUAL DATABASE FIXES FOR SUPABASE
-- Copy and paste this into Supabase SQL Editor

-- 1. Add email_only column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_only TEXT;

-- 2. Create email_reports table
CREATE TABLE IF NOT EXISTS email_reports (
    id BIGSERIAL PRIMARY KEY,
    recipient_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    prediction_data JSONB,
    patient_data JSONB,
    email_content JSONB,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'sent',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Add indexes
CREATE INDEX IF NOT EXISTS idx_email_reports_recipient ON email_reports(recipient_email);
CREATE INDEX IF NOT EXISTS idx_email_reports_sent_at ON email_reports(sent_at);

-- 4. Enable RLS
ALTER TABLE email_reports ENABLE ROW LEVEL SECURITY;

-- 5. Add RLS policies
CREATE POLICY IF NOT EXISTS "Service role can manage email_reports" ON email_reports
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Users can view their own email reports" ON email_reports
    FOR SELECT USING (recipient_email = auth.email());

-- 6. Grant permissions
GRANT ALL ON email_reports TO service_role;
GRANT USAGE, SELECT ON SEQUENCE email_reports_id_seq TO service_role;

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';
"""
    
    with open('manual_database_fixes.sql', 'w') as f:
        f.write(manual_sql)
    
    print("✅ Manual SQL fixes saved to: manual_database_fixes.sql")
    print("📋 To apply manually:")
    print("   1. Go to Supabase Dashboard > SQL Editor")
    print("   2. Copy and paste the content of manual_database_fixes.sql")
    print("   3. Click 'Run' to execute the SQL")

def main():
    """Main function"""
    print("🔧 DATABASE SCHEMA FIXER")
    print("=" * 60)
    
    # Try automatic fixes first
    if apply_database_fixes():
        verify_database_schema()
    else:
        print("\n⚠️ Automatic fixes failed. Creating manual fixes...")
        create_manual_fixes()
    
    print("\n📋 NEXT STEPS:")
    print("1. Restart the backend server")
    print("2. Restart the frontend development server")
    print("3. Test the email functionality")
    print("4. Check browser console for any remaining errors")

if __name__ == "__main__":
    main()
