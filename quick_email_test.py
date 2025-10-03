#!/usr/bin/env python3
"""
Quick test of bulletproof email service for timeout fix verification
"""
import asyncio
from bulletproof_email_service import bulletproof_email_service

async def quick_test():
    print("🧪 QUICK BULLETPROOF EMAIL TEST")
    print("="*50)
    
    # Test connection first
    print("🔗 Testing Gmail connection...")
    connection_result = bulletproof_email_service.test_gmail_connection()
    
    if not connection_result['success']:
        print(f"❌ Connection failed: {connection_result['message']}")
        return
    
    print("✅ Connection successful!")
    
    # Test email sending
    print("\n📧 Testing email delivery...")
    prediction_data = {"prediction": 25000, "confidence": 0.88}
    patient_data = {
        "age": 28, 
        "bmi": 24.5, 
        "gender": "Male", 
        "smoker": "No", 
        "region": "South", 
        "premium_annual_inr": 22000
    }
    
    result = await bulletproof_email_service.send_prediction_email(
        recipient_email="gowthaamankrishna1998@gmail.com",
        prediction_data=prediction_data,
        patient_data=patient_data
    )
    
    print(f"\n📊 RESULT:")
    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    if 'processing_time' in result:
        print(f"Time: {result['processing_time']}s")

if __name__ == "__main__":
    asyncio.run(quick_test())
