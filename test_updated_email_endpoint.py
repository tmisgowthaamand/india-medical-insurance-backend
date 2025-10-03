#!/usr/bin/env python3
"""
Test the updated /send-prediction-email endpoint with bulletproof service
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_email_endpoint():
    """Test the updated email endpoint"""
    print("🧪 TESTING UPDATED EMAIL ENDPOINT")
    print("="*80)
    
    try:
        # Import the app and required models
        from app import send_prediction_email, EmailPredictionRequest
        
        # Create test request
        test_request = EmailPredictionRequest(
            email="gowthaamankrishna1998@gmail.com",
            prediction={"prediction": 25000, "confidence": 0.88},
            patient_data={
                "age": 28,
                "bmi": 24.5,
                "gender": "Male",
                "smoker": "No",
                "region": "South",
                "premium_annual_inr": 22000
            }
        )
        
        print(f"📧 Testing email to: {test_request.email}")
        print(f"💰 Prediction: ₹{test_request.prediction['prediction']:,}")
        print(f"🎯 Confidence: {test_request.prediction['confidence']*100:.1f}%")
        print("-" * 60)
        
        # Call the endpoint
        start_time = datetime.now()
        result = await send_prediction_email(test_request)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n📊 ENDPOINT TEST RESULT")
        print(f"Success: {'✅ YES' if result.success else '❌ NO'}")
        print(f"Message: {result.message}")
        print(f"Processing Time: {processing_time:.2f}s")
        
        if result.success:
            print("\n🎉 EMAIL ENDPOINT TEST PASSED!")
            print("✅ Email should be delivered to Gmail inbox")
            print("📱 Check your email (including spam folder)")
        else:
            print("\n❌ EMAIL ENDPOINT TEST FAILED!")
            print("🔧 Check the error message above")
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_email_endpoint())
