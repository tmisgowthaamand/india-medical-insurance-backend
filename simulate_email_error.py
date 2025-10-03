#!/usr/bin/env python3
"""
Simulate Email Error for MediCare+ Platform
Demonstrates the exact error message format users will see
"""

import requests
import json
import time

def simulate_email_error():
    """Simulate email error by testing with invalid credentials"""
    
    print("="*70)
    print("🧪 SIMULATING EMAIL ERROR - MediCare+ Platform")
    print("="*70)
    
    # Test data
    test_data = {
        "email": "user@gmail.com",
        "prediction": {
            "prediction": 19777.48,
            "confidence": 0.85
        },
        "patient_data": {
            "age": 30,
            "bmi": 25.5,
            "gender": "Male",
            "smoker": "No",
            "region": "North",
            "premium_annual_inr": 20000
        }
    }
    
    print(f"📧 Testing email to: {test_data['email']}")
    print(f"📊 Prediction: ₹{test_data['prediction']['prediction']:,.0f}")
    print()
    
    # Try local backend first
    backends = [
        ("Local Backend", "http://localhost:8001"),
        ("Render Backend", "https://srv-d3b668ogjchc73f9ece0.onrender.com")
    ]
    
    for backend_name, base_url in backends:
        print(f"🔗 Testing {backend_name}: {base_url}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/send-prediction-email",
                json=test_data,
                timeout=60
            )
            
            processing_time = round(time.time() - start_time, 1)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"📧 Success: {result.get('success')}")
                print(f"📧 Message: {result.get('message')}")
                print(f"⏱️ Processing time: {processing_time}s")
                
                # Show what users will see in frontend
                if result.get("success"):
                    print("\n✅ FRONTEND WILL SHOW:")
                    print(f"✅ Email delivered successfully to {test_data['email']}!")
                    print("📧 Check your Gmail inbox now")
                    print("📬 Subject: \"MediCare+ Medical Insurance Report\"")
                    print(f"⏱️ Delivered in {processing_time}s")
                    print("💡 Check spam folder if not in inbox")
                else:
                    print("\n❌ FRONTEND WILL SHOW:")
                    print(f"❌ Email delivery failed to {test_data['email']}")
                    print(f"{result.get('message', 'Gmail delivery error occurred')}")
                    print(f"⏱️ Processing time: {processing_time}s")
                    print("💡 Please try again or use Download option below")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📧 Response: {response.text}")
                
                print("\n❌ FRONTEND WILL SHOW:")
                print(f"❌ Email sending failed: HTTP {response.status_code}")
                print(f"⏱️ Processing time: {processing_time}s")
                print("💡 Please check your internet connection and try again")
                print("📥 Use Download option to save report locally")
            
        except requests.exceptions.ConnectionError:
            print(f"⚠️ {backend_name}: Not available (connection refused)")
            if "localhost" in base_url:
                print("💡 Start local backend with: uvicorn app:app --host 0.0.0.0 --port 8001")
            
            print("\n❌ FRONTEND WILL SHOW:")
            print("❌ Email sending failed: Network error")
            print("⏱️ Processing time: 0.1s")
            print("💡 Please check your internet connection and try again")
            print("📥 Use Download option to save report locally")
            
        except requests.exceptions.Timeout:
            print(f"⏱️ {backend_name}: Timeout (>60s)")
            
            print("\n❌ FRONTEND WILL SHOW:")
            print("❌ Email sending failed: Request timeout")
            print("⏱️ Processing time: 60.0s")
            print("💡 Please check your internet connection and try again")
            print("📥 Use Download option to save report locally")
            
        except Exception as e:
            print(f"❌ {backend_name}: Error - {str(e)}")
            
            print("\n❌ FRONTEND WILL SHOW:")
            print(f"❌ Email sending failed: {str(e)}")
            print("⏱️ Processing time: 0.1s")
            print("💡 Please check your internet connection and try again")
            print("📥 Use Download option to save report locally")
        
        print()
    
    print("="*70)
    print("📋 SUMMARY: EMAIL ERROR MESSAGE FORMATS")
    print("="*70)
    print()
    print("🔴 AUTHENTICATION ERROR:")
    print("❌ Email delivery failed to user@gmail.com")
    print("❌ Gmail connection failed: Authentication error")
    print("⏱️ Processing time: 2.1s")
    print("💡 Please try again or use Download option below")
    print()
    print("🔴 NETWORK ERROR:")
    print("❌ Email sending failed: Network error")
    print("⏱️ Processing time: 0.1s")
    print("💡 Please check your internet connection and try again")
    print("📥 Use Download option to save report locally")
    print()
    print("🔴 TIMEOUT ERROR:")
    print("❌ Email sending failed: Request timeout")
    print("⏱️ Processing time: 60.0s")
    print("💡 Please check your internet connection and try again")
    print("📥 Use Download option to save report locally")
    print()
    print("✅ SUCCESS MESSAGE:")
    print("✅ Email delivered successfully to user@gmail.com!")
    print("📧 Check your Gmail inbox now")
    print("📬 Subject: \"MediCare+ Medical Insurance Report\"")
    print("⏱️ Delivered in 3.2s")
    print("💡 Check spam folder if not in inbox")

if __name__ == "__main__":
    simulate_email_error()
