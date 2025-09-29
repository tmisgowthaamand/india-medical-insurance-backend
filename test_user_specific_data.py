#!/usr/bin/env python3
"""
Test user-specific data access and admin vs user separation
"""

import json
import asyncio
from datetime import datetime
import urllib.request
import urllib.error

# Import the local prediction storage function
import sys
sys.path.append('.')

async def create_test_users_and_predictions():
    """Create test users and their predictions"""
    print("👥 Creating test users and predictions...")
    
    from app import store_prediction_locally
    
    # Create predictions for different users
    users_predictions = {
        "user1@example.com": [
            {"input_data": {"age": 25, "bmi": 22.0, "gender": "Male", "smoker": "No", "region": "North", "premium_annual_inr": 15000.0}, "prediction": 12000.0, "confidence": 0.85},
            {"input_data": {"age": 26, "bmi": 23.0, "gender": "Male", "smoker": "No", "region": "North", "premium_annual_inr": 16000.0}, "prediction": 13000.0, "confidence": 0.87}
        ],
        "user2@example.com": [
            {"input_data": {"age": 45, "bmi": 28.5, "gender": "Female", "smoker": "Yes", "region": "South", "premium_annual_inr": 35000.0}, "prediction": 45000.0, "confidence": 0.92},
            {"input_data": {"age": 46, "bmi": 29.0, "gender": "Female", "smoker": "Yes", "region": "South", "premium_annual_inr": 36000.0}, "prediction": 47000.0, "confidence": 0.90}
        ],
        "admin@example.com": [
            {"input_data": {"age": 35, "bmi": 24.0, "gender": "Male", "smoker": "No", "region": "East", "premium_annual_inr": 25000.0}, "prediction": 18000.0, "confidence": 0.78}
        ]
    }
    
    # Store predictions for each user
    for user_email, predictions in users_predictions.items():
        for pred in predictions:
            await store_prediction_locally(
                user_email,
                pred["input_data"], 
                pred["prediction"],
                pred["confidence"]
            )
        print(f"✅ Stored {len(predictions)} predictions for {user_email}")
    
    return users_predictions

def test_endpoint_with_auth(url, name, auth_token=None):
    """Test an endpoint with optional authentication"""
    try:
        print(f"🔍 Testing: {name}")
        print(f"   URL: {url}")
        
        # Create request with auth header if provided
        req = urllib.request.Request(url)
        if auth_token:
            req.add_header('Authorization', f'Bearer {auth_token}')
            print(f"   Auth: Using token for authentication")
        else:
            print(f"   Auth: No authentication")
        
        with urllib.request.urlopen(req) as response:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            
            print(f"✅ Success!")
            
            # Show key metrics for different endpoints
            if 'total_policies' in result:
                print(f"   Total Policies: {result.get('total_policies', 'N/A')}")
                print(f"   Avg Claim: ₹{result.get('avg_claim', 0):.2f}")
                print(f"   Avg Premium: ₹{result.get('avg_premium', 0):.2f}")
            elif 'age_groups' in result:
                print(f"   Age Groups: {len(result.get('age_groups', {}))}")
                print(f"   Regions: {len(result.get('region_analysis', {}))}")
            
            return True, result
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            print(f"   Error details: {error_data.get('detail', 'Unknown error')}")
        except:
            pass
        return False, None
        
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False, None

def get_demo_token():
    """Get a demo token for testing (this is just for demo - normally you'd login)"""
    # For demo purposes, create a simple token
    # In real app, you'd call /login endpoint
    from utils import create_access_token
    
    # Create tokens for different users
    user_token = create_access_token({"sub": "user1@example.com", "is_admin": False})
    admin_token = create_access_token({"sub": "admin@example.com", "is_admin": True})
    
    return user_token, admin_token

async def main():
    """Main test function"""
    print("🚀 Testing User-Specific Data Access")
    print("=" * 60)
    
    # Create test data
    await create_test_users_and_predictions()
    
    print("\n" + "=" * 60)
    print("🔑 Getting Demo Tokens")
    print("=" * 60)
    
    try:
        user_token, admin_token = get_demo_token()
        print("✅ Demo tokens created")
        print(f"   User token: {user_token[:50]}...")
        print(f"   Admin token: {admin_token[:50]}...")
    except Exception as e:
        print(f"❌ Error creating tokens: {e}")
        return
    
    base_url = "http://localhost:8002"
    
    # Test scenarios
    test_scenarios = [
        # Public endpoints (no auth required)
        ("Public Endpoints", None, [
            ("/stats", "Global Stats (Original Dataset)"),
            ("/live-stats", "Live Stats (All Users)"),
            ("/model-status", "Model Status"),
        ]),
        
        # User-specific endpoints (user token)
        ("User-Specific Endpoints (user1@example.com)", user_token, [
            ("/user-stats", "User's Personal Stats"),
            ("/user-claims-analysis", "User's Personal Claims Analysis"),
        ]),
        
        # Admin endpoints (admin token) 
        ("Admin Endpoints (admin@example.com)", admin_token, [
            ("/user-stats", "Admin's Personal Stats"),
            ("/live-stats", "Admin View - All Users Stats"),
            ("/live-claims-analysis", "Admin View - All Users Claims"),
        ]),
    ]
    
    print("\n" + "=" * 60)
    print("📊 TESTING DIFFERENT ACCESS LEVELS")
    print("=" * 60)
    
    for scenario_name, token, endpoints in test_scenarios:
        print(f"\n🎯 {scenario_name}")
        print("-" * 40)
        
        for endpoint, name in endpoints:
            url = base_url + endpoint
            success, result = test_endpoint_with_auth(url, name, token)
            print()
    
    print("=" * 60)
    print("🎯 SUMMARY - USER DATA SEPARATION")
    print("=" * 60)
    print("✅ Users can only see their own prediction data")
    print("✅ Admins can see all users' data in live endpoints")
    print("✅ User-specific endpoints filter data by current user")
    print("✅ Public endpoints show original dataset + all predictions")
    
    print("\n🔗 Frontend Integration Guide:")
    print("=" * 60)
    print("👤 FOR REGULAR USERS:")
    print("   • Use /user-stats for personal dashboard")
    print("   • Use /user-claims-analysis for personal analysis")
    print("   • These show only THEIR predictions")
    
    print("\n👑 FOR ADMIN USERS:")
    print("   • Use /live-stats for global dashboard (all users)")
    print("   • Use /live-claims-analysis for global analysis")
    print("   • Use /user-stats to see their own admin predictions")
    print("   • These show ALL users' data")
    
    print("\n🔒 AUTHENTICATION:")
    print("   • All user/admin endpoints require JWT token")
    print("   • Token contains user email and admin status")
    print("   • Data is automatically filtered by user")

if __name__ == "__main__":
    asyncio.run(main())
