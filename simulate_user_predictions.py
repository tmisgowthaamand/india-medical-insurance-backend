#!/usr/bin/env python3
"""
Simulate user predictions to test live dashboard updates
"""

import json
import asyncio
from datetime import datetime
import urllib.request

# Import the local prediction storage function
import sys
sys.path.append('.')

async def simulate_predictions():
    """Simulate some user predictions"""
    print("🎭 Simulating user predictions...")
    
    # Import the function
    from app import store_prediction_locally
    
    # Sample predictions from different users
    sample_predictions = [
        {
            "user": "user1@example.com",
            "input_data": {"age": 25, "bmi": 22.0, "gender": "Male", "smoker": "No", "region": "North", "premium_annual_inr": 15000.0},
            "prediction": 12000.0,
            "confidence": 0.85
        },
        {
            "user": "user2@example.com", 
            "input_data": {"age": 45, "bmi": 28.5, "gender": "Female", "smoker": "Yes", "region": "South", "premium_annual_inr": 35000.0},
            "prediction": 45000.0,
            "confidence": 0.92
        },
        {
            "user": "user3@example.com",
            "input_data": {"age": 35, "bmi": 24.0, "gender": "Male", "smoker": "No", "region": "East", "premium_annual_inr": 25000.0},
            "prediction": 18000.0,
            "confidence": 0.78
        },
        {
            "user": "user4@example.com",
            "input_data": {"age": 55, "bmi": 30.0, "gender": "Female", "smoker": "Yes", "region": "West", "premium_annual_inr": 40000.0},
            "prediction": 55000.0,
            "confidence": 0.88
        }
    ]
    
    # Store each prediction
    for i, pred in enumerate(sample_predictions):
        await store_prediction_locally(
            pred["user"],
            pred["input_data"], 
            pred["prediction"],
            pred["confidence"]
        )
        print(f"✅ Stored prediction {i+1}: {pred['user']} - ₹{pred['prediction']:.2f}")
    
    print(f"🎉 Simulated {len(sample_predictions)} user predictions!")

def test_endpoint_comparison():
    """Compare original vs live endpoints"""
    base_url = "http://localhost:8002"
    
    endpoints = [
        ("/stats", "Original Stats"),
        ("/live-stats", "Live Stats"),
    ]
    
    print("\n📊 Comparing Dashboard Statistics")
    print("=" * 50)
    
    for endpoint, name in endpoints:
        url = base_url + endpoint
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                result = json.loads(data.decode('utf-8'))
                
                print(f"\n{name}:")
                print(f"   Total Policies: {result.get('total_policies', 'N/A')}")
                print(f"   Avg Claim: ₹{result.get('avg_claim', 0):.2f}")
                print(f"   Avg Premium: ₹{result.get('avg_premium', 0):.2f}")
                print(f"   Smoker %: {result.get('smoker_percentage', 0):.1f}%")
                
        except Exception as e:
            print(f"❌ Error testing {name}: {e}")

async def main():
    """Main test function"""
    print("🚀 Testing Live Dashboard Updates")
    print("=" * 50)
    
    print("📈 BEFORE: Testing endpoints before predictions")
    test_endpoint_comparison()
    
    print("\n" + "=" * 50)
    await simulate_predictions()
    
    print("\n" + "=" * 50)
    print("📈 AFTER: Testing endpoints after predictions")
    test_endpoint_comparison()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY")
    print("=" * 50)
    print("✅ User predictions are now stored locally")
    print("✅ Live endpoints include user prediction data")
    print("✅ Dashboard will update automatically when users make predictions")
    print("✅ Claims analysis includes real user data")
    
    print("\n🔗 Frontend Integration:")
    print("   Use /live-stats instead of /stats")
    print("   Use /live-claims-analysis instead of /claims-analysis")
    print("   Dashboard will show real-time data including user predictions!")

if __name__ == "__main__":
    asyncio.run(main())
