#!/usr/bin/env python3
import asyncio
from enhanced_email_service import enhanced_email_service

async def quick_test():
    print("Quick Email Service Test")
    print("-" * 30)
    
    # Test data
    prediction_data = {"prediction": 25000, "confidence": 0.85}
    patient_data = {"age": 30, "bmi": 22.5, "gender": "Male", "smoker": "No", "region": "Southeast", "premium_annual_inr": 15000}
    
    # Test immediate feedback
    result = await enhanced_email_service.send_prediction_email_with_immediate_feedback(
        recipient_email="test@example.com",
        prediction_data=prediction_data,
        patient_data=patient_data
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    print(f"Immediate: {result.get('immediate')}")

if __name__ == "__main__":
    asyncio.run(quick_test())
