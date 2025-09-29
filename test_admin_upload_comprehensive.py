#!/usr/bin/env python3
"""
Comprehensive test for admin upload functionality with sample_medical_insurance_data.csv
"""

import urllib.request
import urllib.error
import json
import os
import mimetypes

def get_admin_token():
    """Get admin token for testing"""
    try:
        from utils import create_access_token
        admin_token = create_access_token({"sub": "admin@example.com", "is_admin": True})
        return admin_token
    except Exception as e:
        print(f"❌ Error creating admin token: {e}")
        return None

def create_multipart_form_data(file_path, field_name='file'):
    """Create multipart form data for file upload"""
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        f'Content-Type: {content_type}\r\n'
        f'\r\n'
    ).encode('utf-8')
    
    body += file_content
    body += f'\r\n--{boundary}--\r\n'.encode('utf-8')
    
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body))
    }
    
    return body, headers

def test_admin_upload_with_auth():
    """Test admin upload with proper authentication"""
    print("🔐 Testing admin upload with authentication...")
    
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot test without admin token")
        return False
    
    csv_file = "data/sample_medical_insurance_data.csv"
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    try:
        # Create multipart form data
        body, headers = create_multipart_form_data(csv_file)
        
        # Add authorization header
        headers['Authorization'] = f'Bearer {admin_token}'
        
        # Create request
        url = "http://localhost:8002/admin/upload"
        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        
        print(f"📤 Uploading {csv_file} to {url}")
        print(f"🔑 Using admin token: {admin_token[:50]}...")
        
        with urllib.request.urlopen(req) as response:
            response_data = response.read()
            result = json.loads(response_data.decode('utf-8'))
            
            print("✅ Upload successful!")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Dataset rows: {result.get('dataset_rows', 'Unknown')}")
            print(f"   Training completed: {result.get('training_completed', 'Unknown')}")
            print(f"   File path: {result.get('file_path', 'Unknown')}")
            
            return True
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            print(f"   Error details: {error_data}")
        except:
            print(f"   Raw error: {error_body}")
        return False
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def test_endpoints_after_upload():
    """Test that endpoints work after upload"""
    print("\n📊 Testing endpoints after upload...")
    
    base_url = "http://localhost:8002"
    endpoints = [
        "/stats",
        "/live-stats",
        "/claims-analysis", 
        "/live-claims-analysis",
        "/model-status"
    ]
    
    success_count = 0
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            print(f"🔍 Testing: {endpoint}")
            
            with urllib.request.urlopen(url) as response:
                data = response.read()
                result = json.loads(data.decode('utf-8'))
                
                print(f"✅ Success")
                if 'total_policies' in result:
                    print(f"   Total Policies: {result.get('total_policies')}")
                    print(f"   Avg Claim: ₹{result.get('avg_claim', 0):.2f}")
                elif 'status' in result:
                    print(f"   Status: {result.get('status')}")
                
                success_count += 1
                
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print(f"\n📈 Endpoints working: {success_count}/{len(endpoints)}")
    return success_count == len(endpoints)

def test_file_validation():
    """Test file validation"""
    print("\n📁 Testing file validation...")
    
    csv_file = "data/sample_medical_insurance_data.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ Test file not found: {csv_file}")
        return False
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_file)
        
        print(f"✅ File validation passed")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Check required columns
        required_columns = ['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr', 'claim_amount_inr']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        print("✅ All required columns present")
        return True
        
    except Exception as e:
        print(f"❌ File validation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Comprehensive Admin Upload Test")
    print("=" * 60)
    
    # Test 1: File validation
    file_valid = test_file_validation()
    
    # Test 2: Admin upload
    upload_success = False
    if file_valid:
        upload_success = test_admin_upload_with_auth()
    
    # Test 3: Endpoints after upload
    endpoints_working = False
    if upload_success:
        endpoints_working = test_endpoints_after_upload()
    
    print(f"\n{'=' * 60}")
    print("🏁 COMPREHENSIVE TEST RESULTS")
    print(f"{'=' * 60}")
    
    results = [
        ("File Validation", file_valid),
        ("Admin Upload", upload_success),
        ("Endpoints After Upload", endpoints_working)
    ]
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Admin upload is working correctly")
        print("✅ sample_medical_insurance_data.csv uploads successfully")
        print("✅ Claims analysis and admin system are working")
    else:
        print("⚠️ Some tests failed")
        if not file_valid:
            print("   • File validation issues")
        if not upload_success:
            print("   • Admin upload is failing (500 error)")
        if not endpoints_working:
            print("   • Endpoints not working after upload")
    
    print(f"\n🔗 Next Steps:")
    if upload_success:
        print("   • Upload functionality is working")
        print("   • Try uploading via your frontend admin panel")
    else:
        print("   • Check server logs for detailed error information")
        print("   • Verify admin authentication")

if __name__ == "__main__":
    main()
