#!/usr/bin/env python3
"""
Quick Email Test - Test the fixed email functionality
"""

import requests
import json

def test_email():
    """Quick test of email endpoint"""
    
    url = "http://localhost:8001/send-prediction-email"
    
    data = {
        "email": "gokrishna98@gmail.com",
        "prediction": {
            "prediction": 45000,
            "confidence": 0.87
        },
        "patient_data": {
            "age": 35,
            "bmi": 24.5,
            "gender": "Male",
            "smoker": "No",
            "region": "North",
            "premium_annual_inr": 25000
        }
    }
    
    try:
        print("🧪 Testing email endpoint...")
        response = requests.post(url, json=data, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Message: {result.get('message')}")
            return True
        else:
            print("❌ FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_email()
