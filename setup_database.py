#!/usr/bin/env python3
"""
Script to set up the database schema in Supabase
Run this after configuring your Supabase credentials
"""
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

async def setup_database_schema():
    """Set up the database schema in Supabase"""
    print("🗄️ Setting up Supabase Database Schema")
    print("=" * 40)
    
    # Check credentials
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_key:
        print("❌ Missing Supabase credentials in .env file")
        print("Please run setup_supabase.py first")
        return False
    
    if url == "https://your-project.supabase.co" or service_key == "your_service_role_key_here":
        print("❌ Placeholder credentials detected")
        print("Please update your .env file with actual Supabase credentials")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(url, service_key)
        print("✅ Connected to Supabase")
        
        # Read schema file
        schema_file = "supabase_schema.sql"
        if not os.path.exists(schema_file):
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("📄 Read database schema file")
        
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"🔧 Executing {len(statements)} SQL statements...")
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            try:
                # Execute SQL statement
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                print(f"✅ Statement {i}/{len(statements)} executed successfully")
                success_count += 1
                
            except Exception as e:
                # Some statements might fail if they already exist, which is okay
                error_msg = str(e).lower()
                if any(keyword in error_msg for keyword in ['already exists', 'duplicate', 'relation exists']):
                    print(f"⚠️  Statement {i}/{len(statements)} - Already exists (skipped)")
                else:
                    print(f"❌ Statement {i}/{len(statements)} failed: {e}")
                    error_count += 1
        
        print(f"\n📊 Schema setup complete!")
        print(f"✅ Successful: {success_count}")
        print(f"⚠️  Skipped: {len(statements) - success_count - error_count}")
        print(f"❌ Errors: {error_count}")
        
        if error_count == 0:
            print("\n🎉 Database schema set up successfully!")
            return True
        else:
            print(f"\n⚠️  Schema setup completed with {error_count} errors")
            print("You may need to run some statements manually in Supabase SQL Editor")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\n💡 Alternative approach:")
        print("1. Go to your Supabase dashboard")
        print("2. Open SQL Editor")
        print("3. Copy contents from supabase_schema.sql")
        print("4. Paste and run in SQL Editor")
        return False

async def verify_tables():
    """Verify that all tables were created"""
    print("\n🔍 Verifying database tables...")
    
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    try:
        supabase: Client = create_client(url, service_key)
        
        # Check for tables
        expected_tables = ['users', 'datasets', 'dataset_rows', 'model_metadata', 'predictions', 'app_logs']
        
        for table in expected_tables:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"✅ Table '{table}' exists and accessible")
            except Exception as e:
                print(f"❌ Table '{table}' not found or not accessible: {e}")
        
        # Insert default users if they don't exist
        try:
            # Check if admin user exists
            admin_check = supabase.table('users').select('*').eq('email', 'admin@example.com').execute()
            
            if not admin_check.data:
                # Insert default admin user
                admin_user = {
                    'email': 'admin@example.com',
                    'password': 'admin123',
                    'is_admin': True
                }
                supabase.table('users').insert(admin_user).execute()
                print("✅ Default admin user created")
            else:
                print("✅ Admin user already exists")
                
        except Exception as e:
            print(f"⚠️  Could not create default users: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

if __name__ == "__main__":
    print("🏥 India Medical Insurance Dashboard")
    print("Database Schema Setup")
    print("=" * 50)
    
    # Run setup
    success = asyncio.run(setup_database_schema())
    
    if success:
        # Verify tables
        asyncio.run(verify_tables())
        
        print("\n🚀 Next steps:")
        print("1. Test integration: python test_supabase_integration.py")
        print("2. Start application: cd .. && python start.py")
    else:
        print("\n💡 Manual setup required:")
        print("1. Copy contents from supabase_schema.sql")
        print("2. Paste into Supabase SQL Editor")
        print("3. Run the SQL statements")
