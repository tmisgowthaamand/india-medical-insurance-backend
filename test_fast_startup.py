#!/usr/bin/env python3
"""
Test fast startup optimizations
"""

import time
import requests
import subprocess
import sys
import os

def test_local_startup():
    """Test local startup speed"""
    print("🚀 Testing local startup speed...")
    
    start_time = time.time()
    
    # Start the server
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app:app", 
        "--host", "127.0.0.1", "--port", "8002"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to be ready
    max_wait = 30  # seconds
    server_ready = False
    
    for i in range(max_wait):
        try:
            response = requests.get("http://127.0.0.1:8002/", timeout=2)
            if response.status_code == 200:
                server_ready = True
                startup_time = time.time() - start_time
                print(f"✅ Server started in {startup_time:.2f} seconds")
                print(f"Response: {response.json()}")
                break
        except:
            time.sleep(1)
    
    # Cleanup
    process.terminate()
    process.wait()
    
    if not server_ready:
        print("❌ Server failed to start within 30 seconds")
        return False
    
    return startup_time < 15  # Should start within 15 seconds

def test_render_endpoint():
    """Test the Render endpoint"""
    print("\n🌐 Testing Render endpoint...")
    
    try:
        response = requests.get("https://india-medical-insurance-backend.onrender.com/", timeout=10)
        if response.status_code == 200:
            print("✅ Render endpoint is working!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Render endpoint returned status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("⚠️ Render endpoint timed out (this is expected during cold starts)")
        return False
    except Exception as e:
        print(f"❌ Error testing Render endpoint: {e}")
        return False

def main():
    """Main test function"""
    print("🏥 Fast Startup Test")
    print("=" * 40)
    
    # Change to backend directory
    if not os.path.exists("app.py"):
        if os.path.exists("backend/app.py"):
            os.chdir("backend")
        else:
            print("❌ Cannot find app.py")
            return
    
    # Test local startup
    local_ok = test_local_startup()
    
    # Test Render endpoint
    render_ok = test_render_endpoint()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"Local Startup: {'✅ FAST' if local_ok else '❌ SLOW'}")
    print(f"Render Endpoint: {'✅ WORKING' if render_ok else '⚠️ ISSUE'}")
    
    if local_ok:
        print("\n🎉 Optimizations successful! Fast startup achieved.")
    else:
        print("\n⚠️ Startup still slow. May need further optimization.")

if __name__ == "__main__":
    main()
