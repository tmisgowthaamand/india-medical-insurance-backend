#!/usr/bin/env python3
"""
Backend Status Checker
Quick script to verify backend server status
"""

import requests
import json
from datetime import datetime

def check_backend_status():
    """Check if backend server is running and responding"""
    
    print("=" * 50)
    print("BACKEND STATUS CHECKER")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test main endpoint
    try:
        print("\n🔍 Testing main endpoint...")
        response = requests.get("http://localhost:8001/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Main endpoint: WORKING")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
        else:
            print(f"❌ Main endpoint: ERROR (Status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Main endpoint: CONNECTION FAILED")
        print("   Backend server is not running on port 8001")
        return False
    except Exception as e:
        print(f"❌ Main endpoint: ERROR - {e}")
        return False
    
    # Test API docs endpoint
    try:
        print("\n🔍 Testing API docs...")
        response = requests.get("http://localhost:8001/docs", timeout=5)
        
        if response.status_code == 200:
            print("✅ API docs: ACCESSIBLE")
            print("   URL: http://localhost:8001/docs")
        else:
            print(f"⚠️ API docs: Status {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ API docs: ERROR - {e}")
    
    # Test health endpoint (if exists)
    try:
        print("\n🔍 Testing health endpoint...")
        response = requests.get("http://localhost:8001/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Health endpoint: WORKING")
        else:
            print(f"⚠️ Health endpoint: Status {response.status_code}")
            
    except Exception:
        print("⚠️ Health endpoint: Not available")
    
    print("\n" + "=" * 50)
    print("✅ BACKEND SERVER IS RUNNING SUCCESSFULLY!")
    print("=" * 50)
    print("🌐 Server URL: http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    print("🔧 Admin Panel: Available via frontend")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = check_backend_status()
    if not success:
        print("\n❌ Backend server check failed!")
        print("💡 Try running: fix_terminal.ps1 or quick_terminal_fix.bat")
        exit(1)
    else:
        print("\n🎉 All systems operational!")
