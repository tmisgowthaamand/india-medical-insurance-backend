#!/usr/bin/env python3
"""
Test API Email Endpoint
Tests the /send-prediction-email and /test-email endpoints
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_email_endpoints():
    """Test both email endpoints"""
    print("🧪 TESTING EMAIL API ENDPOINTS")
    print("="*60)
    
    base_url = "http://localhost:8001"  # Local backend
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Test Email Endpoint
        print("📧 TEST 1: /test-email endpoint")
        try:
            async with session.post(f"{base_url}/test-email") as response:
                result = await response.json()
                print(f"Status: {response.status}")
                print(f"Success: {'✅' if result.get('success') else '❌'}")
                print(f"Message: {result.get('message')}")
                print(f"Processing Time: {result.get('processing_time', 'N/A')}s")
                print(f"Recipient: {result.get('recipient', 'N/A')}")
        except Exception as e:
            print(f"❌ Test email endpoint failed: {e}")
        
        print()
        
        # Test 2: Send Prediction Email Endpoint
        print("📊 TEST 2: /send-prediction-email endpoint")
        
        prediction_request = {
            "email": "perivihari8@gmail.com",
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
        
        try:
            async with session.post(
                f"{base_url}/send-prediction-email",
                json=prediction_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                print(f"Status: {response.status}")
                print(f"Success: {'✅' if result.get('success') else '❌'}")
                print(f"Message: {result.get('message')}")
        except Exception as e:
            print(f"❌ Prediction email endpoint failed: {e}")
    
    print()
    print("="*60)
    print("🎯 EMAIL API ENDPOINT TESTS COMPLETED")
    print("✅ Check perivihari8@gmail.com inbox for emails")
    print("="*60)

if __name__ == "__main__":
    print("⚠️  Make sure the backend server is running on localhost:8001")
    print("   Run: uvicorn app:app --host 0.0.0.0 --port 8001")
    print()
    
    asyncio.run(test_email_endpoints())
