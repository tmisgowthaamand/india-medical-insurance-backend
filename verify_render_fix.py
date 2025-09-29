#!/usr/bin/env python3
"""
Verify Render Configuration Fix
Tests if the Supabase configuration issue has been resolved
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_local_config():
    """Test local environment configuration"""
    print("🔍 Testing Local Configuration...")
    print("-" * 40)
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    if supabase_url:
        print(f"  Value: {supabase_url}")
    
    print(f"SUPABASE_ANON_KEY: {'✅ Set' if anon_key else '❌ Missing'}")
    if anon_key:
        print(f"  Length: {len(anon_key)} characters")
    
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if service_key else '❌ Missing'}")
    if service_key:
        print(f"  Length: {len(service_key)} characters")
    
    return all([supabase_url, anon_key, service_key])

def test_database_client():
    """Test database client initialization"""
    print("\n🔍 Testing Database Client...")
    print("-" * 40)
    
    try:
        from database import supabase_client
        
        if supabase_client.is_enabled():
            print("✅ Supabase client initialized successfully")
            print(f"   URL: {supabase_client.url}")
            print(f"   Client: {type(supabase_client.client).__name__}")
            return True
        else:
            print("❌ Supabase client not enabled")
            print("   This indicates environment variables are not properly set")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing database client: {e}")
        return False

def test_render_backend():
    """Test the deployed Render backend"""
    print("\n🔍 Testing Render Backend...")
    print("-" * 40)
    
    backend_url = "https://india-medical-insurance-backend.onrender.com"
    
    # Test health endpoint
    try:
        print("Testing /health endpoint...")
        response = requests.get(f"{backend_url}/health", timeout=15)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Model Loaded: {data.get('model_loaded')}")
            print(f"   CORS Origins: {data.get('cors_origins')}")
            return True
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_signup_endpoint():
    """Test signup endpoint to verify database connectivity"""
    print("\n🔍 Testing Signup Endpoint...")
    print("-" * 40)
    
    backend_url = "https://india-medical-insurance-backend.onrender.com"
    
    # Test with a unique email
    from datetime import datetime
    test_email = f"test_{datetime.now().strftime('%H%M%S')}@medicare.com"
    
    test_data = {
        "email": test_email,
        "password": "test123"
    }
    
    try:
        response = requests.post(
            f"{backend_url}/signup",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 200:
            print("✅ Signup endpoint working - Database connected")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            print("✅ Signup endpoint working - User already exists")
            return True
        elif response.status_code == 500:
            print("❌ 500 Error - Database tables still missing")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Signup test error: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🏥 MediCare+ Render Configuration Verification")
    print("=" * 60)
    
    tests = [
        ("Local Configuration", test_local_config),
        ("Database Client", test_database_client),
        ("Render Backend Health", test_render_backend),
        ("Database Connectivity", test_signup_endpoint)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Render configuration fix successful")
        print("✅ Backend is fully operational")
        print("✅ Database connectivity confirmed")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        
        if not results.get("Local Configuration"):
            print("💡 Check your .env file has correct Supabase variables")
        
        if not results.get("Database Client"):
            print("💡 Verify environment variables in Render dashboard")
        
        if not results.get("Render Backend Health"):
            print("💡 Check Render service logs for startup errors")
        
        if not results.get("Database Connectivity"):
            print("💡 Run the SQL script in Supabase to create missing tables")

if __name__ == "__main__":
    main()
