#!/usr/bin/env python3
"""
Test Email Functionality for Existing Users
Tests that emails are sent successfully even when email already exists in users table
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"  # Local backend
# BASE_URL = "https://srv-d3b668ogjchc73f9ece0.onrender.com"  # Render backend

def test_email_for_existing_user():
    """Test email sending for users that already exist in the database"""
    
    print("🧪 Testing Email Functionality for Existing Users")
    print("=" * 60)
    
    # Test data - these emails should already exist in the users table
    test_emails = [
        "gowthaamankrishna1998@gmail.com",
        "perivihari8@gmail.com", 
        "gokrishna98@gmail.com",
        "admin@example.com"
    ]
    
    # Sample prediction data
    prediction_data = {
        "prediction": 28500.75,
        "confidence": 0.87
    }
    
    # Sample patient data
    patient_data = {
        "age": 32,
        "bmi": 24.8,
        "gender": "Male",
        "smoker": "No",
        "region": "North",
        "premium_annual_inr": 22000
    }
    
    results = []
    
    for email in test_emails:
        print(f"\n📧 Testing email send to: {email}")
        print("-" * 40)
        
        try:
            # Prepare email request
            email_request = {
                "email": email,
                "prediction": prediction_data,
                "patient_data": patient_data
            }
            
            # Send email request
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/send-prediction-email",
                json=email_request,
                timeout=120  # 2 minute timeout
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS: {result.get('message', 'Email sent')}")
                print(f"⏱️ Response time: {response_time:.2f}s")
                
                results.append({
                    "email": email,
                    "status": "success",
                    "message": result.get('message'),
                    "response_time": response_time
                })
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
                results.append({
                    "email": email,
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response_time
                })
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: Request timed out after 120 seconds")
            results.append({
                "email": email,
                "status": "timeout",
                "error": "Request timeout"
            })
            
        except requests.exceptions.ConnectionError:
            print(f"🔌 CONNECTION ERROR: Could not connect to backend")
            results.append({
                "email": email,
                "status": "connection_error",
                "error": "Connection failed"
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                "email": email,
                "status": "error",
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] != "success"]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        avg_time = sum(r.get("response_time", 0) for r in successful) / len(successful)
        print(f"⏱️ Average response time: {avg_time:.2f}s")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {result['email']}: {result['status']}")
        if "message" in result:
            print(f"   Message: {result['message']}")
        if "error" in result:
            print(f"   Error: {result['error']}")
        if "response_time" in result:
            print(f"   Time: {result['response_time']:.2f}s")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"email_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "test_timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "total_tests": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return len(successful) == len(results)

def test_health_endpoint():
    """Test if backend is responding"""
    print("🏥 Testing backend health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend is healthy: {health_data.get('status')}")
            return True
        else:
            print(f"❌ Backend health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Email Functionality Test for Existing Users")
    print(f"🔗 Backend URL: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test backend health first
    if not test_health_endpoint():
        print("❌ Backend is not responding. Please start the backend server first.")
        exit(1)
    
    # Run email tests
    success = test_email_for_existing_user()
    
    if success:
        print("\n🎉 All email tests passed!")
        exit(0)
    else:
        print("\n⚠️ Some email tests failed. Check the results above.")
        exit(1)
