#!/usr/bin/env python3
"""
Quick setup script for Supabase configuration
Run this after creating your Supabase project
"""
import os
import sys

def setup_supabase():
    """Interactive setup for Supabase credentials"""
    print("🚀 Supabase Configuration Setup")
    print("=" * 40)
    print("Your organization: ulvqxgvdoggtszgbdzoh")
    print("Dashboard: https://supabase.com/dashboard/org/ulvqxgvdoggtszgbdzoh")
    print()
    
    # Get credentials from user
    print("Please enter your Supabase project credentials:")
    print("(You can find these in Settings → API in your Supabase dashboard)")
    print()
    
    supabase_url = input("Project URL (https://xxxxx.supabase.co): ").strip()
    if not supabase_url.startswith('https://') or not supabase_url.endswith('.supabase.co'):
        print("❌ Invalid URL format. Should be: https://xxxxx.supabase.co")
        return False
    
    anon_key = input("Anon public key (starts with eyJ...): ").strip()
    if not anon_key.startswith('eyJ'):
        print("❌ Invalid anon key format. Should start with 'eyJ'")
        return False
    
    service_key = input("Service role key (starts with eyJ...): ").strip()
    if not service_key.startswith('eyJ'):
        print("❌ Invalid service role key format. Should start with 'eyJ'")
        return False
    
    # Update backend .env
    backend_env = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_ANON_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_key}

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
ENVIRONMENT=development
"""
    
    # Update frontend .env
    frontend_env = f"""# Supabase Configuration
VITE_SUPABASE_URL={supabase_url}
VITE_SUPABASE_ANON_KEY={anon_key}

# API Configuration
VITE_API_BASE_URL=http://localhost:8001
"""
    
    try:
        # Write backend .env
        with open('backend/.env', 'w') as f:
            f.write(backend_env)
        print("✅ Updated backend/.env")
        
        # Write frontend .env
        with open('frontend/.env', 'w') as f:
            f.write(frontend_env)
        print("✅ Updated frontend/.env")
        
        print("\n🎉 Configuration complete!")
        print("\nNext steps:")
        print("1. Set up database schema in Supabase SQL Editor")
        print("2. Run: cd backend && python test_supabase_integration.py")
        print("3. Start the application: python start.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing configuration files: {e}")
        return False

def show_schema_instructions():
    """Show instructions for setting up the database schema"""
    print("\n📊 Database Schema Setup")
    print("=" * 30)
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Click 'New Query'")
    print("4. Copy the contents from: backend/supabase_schema.sql")
    print("5. Paste into SQL Editor and click 'Run'")
    print("\nThis will create all necessary tables and security policies.")

def test_configuration():
    """Test the Supabase configuration"""
    print("\n🧪 Testing Configuration")
    print("=" * 25)
    
    try:
        os.chdir('backend')
        result = os.system('python test_supabase_integration.py')
        if result == 0:
            print("✅ Configuration test passed!")
        else:
            print("❌ Configuration test failed. Check your credentials.")
    except Exception as e:
        print(f"❌ Error running test: {e}")

if __name__ == "__main__":
    print("🏥 India Medical Insurance Dashboard")
    print("Supabase Integration Setup")
    print("=" * 50)
    
    if not os.path.exists('backend') or not os.path.exists('frontend'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Setup configuration
    if setup_supabase():
        show_schema_instructions()
        
        # Ask if user wants to test
        test_now = input("\nWould you like to test the configuration now? (y/n): ").strip().lower()
        if test_now == 'y':
            test_configuration()
    
    print("\n📚 For detailed instructions, see: YOUR_SUPABASE_SETUP.md")
