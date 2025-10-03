#!/usr/bin/env python3
"""
Test script to verify the timeout fix for email delivery
Tests both local and Render backend email functionality
"""

import asyncio
import time
import requests
import json
from datetime import datetime

class EmailTimeoutTester:
    def __init__(self):
        self.local_backend = "http://localhost:8001"
        self.render_backend = "https://srv-d3b668ogjchc73f9ece0-latest.onrender.com"
        self.test_email = "gowthaamankrishna1998@gmail.com"
        
    def test_health_endpoint(self, backend_url):
        """Test health endpoint with timeout"""
        print(f"🏥 Testing health endpoint: {backend_url}")
        
        try:
            start_time = time.time()
            response = requests.get(f"{backend_url}/health", timeout=45)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Health check passed in {duration:.2f}s")
                print(f"   📊 Response: {response.json()}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            print(f"   ⏰ Health check timed out after {duration:.2f}s")
            return False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
    
    def test_email_endpoint(self, backend_url):
        """Test email endpoint with proper timeout"""
        print(f"📧 Testing email endpoint: {backend_url}")
        
        # Prepare test data
        email_data = {
            "email": self.test_email,
            "prediction": {
                "prediction": 25000,
                "confidence": 0.88
            },
            "patient_data": {
                "age": 28,
                "bmi": 24.5,
                "gender": "Male",
                "smoker": "No",
                "region": "South",
                "premium_annual_inr": 22000,
                "report_generated": datetime.now().isoformat()
            }
        }
        
        try:
            start_time = time.time()
            
            # Use longer timeout for Render services
            timeout = 150 if 'onrender.com' in backend_url else 60
            print(f"   ⏱️ Using {timeout}s timeout for email request")
            
            response = requests.post(
                f"{backend_url}/send-prediction-email",
                json=email_data,
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Email request completed in {duration:.2f}s")
                print(f"   📊 Success: {result.get('success', False)}")
                print(f"   💬 Message: {result.get('message', 'No message')}")
                return result.get('success', False)
            else:
                print(f"   ❌ Email request failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            print(f"   ⏰ Email request timed out after {duration:.2f}s")
            return False
        except Exception as e:
            print(f"   ❌ Email request error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive test of both backends"""
        print("🧪 COMPREHENSIVE EMAIL TIMEOUT FIX TEST")
        print("="*60)
        print(f"📧 Test email: {self.test_email}")
        print(f"🕐 Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {}
        
        # Test local backend
        print("🏠 TESTING LOCAL BACKEND")
        print("-" * 30)
        local_health = self.test_health_endpoint(self.local_backend)
        local_email = False
        
        if local_health:
            local_email = self.test_email_endpoint(self.local_backend)
        else:
            print("   ⚠️ Skipping email test - health check failed")
        
        results['local'] = {
            'health': local_health,
            'email': local_email
        }
        
        print()
        
        # Test Render backend
        print("☁️ TESTING RENDER BACKEND")
        print("-" * 30)
        render_health = self.test_health_endpoint(self.render_backend)
        render_email = False
        
        if render_health:
            render_email = self.test_email_endpoint(self.render_backend)
        else:
            print("   ⚠️ Skipping email test - health check failed")
        
        results['render'] = {
            'health': render_health,
            'email': render_email
        }
        
        print()
        
        # Summary
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        print(f"🏠 Local Backend:")
        print(f"   Health: {'✅ PASS' if results['local']['health'] else '❌ FAIL'}")
        print(f"   Email:  {'✅ PASS' if results['local']['email'] else '❌ FAIL'}")
        print()
        print(f"☁️ Render Backend:")
        print(f"   Health: {'✅ PASS' if results['render']['health'] else '❌ FAIL'}")
        print(f"   Email:  {'✅ PASS' if results['render']['email'] else '❌ FAIL'}")
        print()
        
        # Recommendations
        if results['render']['email']:
            print("🎉 SUCCESS! Email functionality is working on Render!")
            print(f"📧 Check {self.test_email} inbox for the test email")
        elif results['local']['email']:
            print("⚠️ Local backend works, but Render has issues")
            print("🔧 Check Render environment variables and logs")
        else:
            print("❌ Email functionality needs attention")
            print("🔧 Check backend configuration and email service setup")
        
        return results

def main():
    """Main test function"""
    tester = EmailTimeoutTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if results['render']['email'] or results['local']['email']:
        print("\n✅ At least one backend is working - test passed!")
        exit(0)
    else:
        print("\n❌ No backends are working - test failed!")
        exit(1)

if __name__ == "__main__":
    main()
