#!/usr/bin/env python3
"""
Test script to verify the upload functionality works correctly
"""
import requests
import os

# Configuration
BASE_URL = "http://localhost:8001"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def test_upload():
    """Test the file upload functionality"""
    print("Testing upload functionality...")
    
    # Step 1: Login as admin
    print("1. Logging in as admin...")
    login_data = {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/login", data=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login successful")
    
    # Step 2: Test upload with existing sample file
    print("2. Testing file upload...")
    sample_file_path = "data/sample_medical_insurance_data.csv"
    
    if not os.path.exists(sample_file_path):
        print(f"Sample file not found: {sample_file_path}")
        return False
    
    with open(sample_file_path, 'rb') as f:
        files = {"file": ("test_upload.csv", f, "text/csv")}
        upload_response = requests.post(f"{BASE_URL}/admin/upload", files=files, headers=headers)
    
    print(f"Upload response: {upload_response.status_code}")
    print(f"Upload message: {upload_response.json() if upload_response.status_code == 200 else upload_response.text}")
    
    if upload_response.status_code == 200:
        print("✓ Upload successful")
        return True
    else:
        print(f"✗ Upload failed: {upload_response.status_code}")
        return False

def test_retrain():
    """Test the retrain functionality"""
    print("\nTesting retrain functionality...")
    
    # Login as admin
    login_data = {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/login", data=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test retrain
    retrain_response = requests.post(f"{BASE_URL}/admin/retrain", headers=headers)
    print(f"Retrain response: {retrain_response.status_code}")
    print(f"Retrain message: {retrain_response.json() if retrain_response.status_code == 200 else retrain_response.text}")
    
    if retrain_response.status_code == 200:
        print("✓ Retrain successful")
        return True
    else:
        print(f"✗ Retrain failed: {retrain_response.status_code}")
        return False

if __name__ == "__main__":
    print("Starting upload and training tests...")
    print("=" * 50)
    
    # Test upload
    upload_success = test_upload()
    
    # Test retrain
    retrain_success = test_retrain()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Upload: {'✓ PASS' if upload_success else '✗ FAIL'}")
    print(f"Retrain: {'✓ PASS' if retrain_success else '✗ FAIL'}")
