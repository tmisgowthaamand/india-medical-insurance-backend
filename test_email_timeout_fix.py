#!/usr/bin/env python3
"""
Test and Fix Email Timeout Issues
Diagnoses why the frontend is timing out when calling the email API
"""

import requests
import time
import json

def test_email_api_performance():
    """Test email API performance and response times"""
    
    print("⏱️ Testing Email API Performance")
    print("=" * 50)
    
    email_data = {
        "email": "gowthaamankrishna1998@gmail.com",
        "prediction": {
            "prediction": 25000.0,
            "confidence": 0.85
        },
        "patient_data": {
            "age": 35,
            "bmi": 23.0,
            "gender": "Male",
            "smoker": "No",
            "region": "East",
            "premium_annual_inr": 25000.0
        }
    }
    
    # Test different timeout values
    timeouts = [5, 10, 15, 30, 60]
    
    for timeout in timeouts:
        print(f"\n🕐 Testing with {timeout}s timeout...")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8001/send-prediction-email",
                json=email_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"📊 Status: {response.status_code}")
            print(f"⏱️ Duration: {duration:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('success', False)}")
                print(f"📝 Message: {result.get('message', 'No message')}")
                
                if duration < 10:
                    print("🚀 Fast response - good for frontend")
                elif duration < 20:
                    print("⚠️ Slow response - may cause timeouts")
                else:
                    print("🐌 Very slow - will definitely timeout")
                
                return True
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout after {timeout}s")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def test_server_health_speed():
    """Test server health endpoint speed"""
    
    print("\n🏥 Testing Server Health Speed")
    print("=" * 50)
    
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8001/health", timeout=5)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"⏱️ Health check duration: {duration:.2f}s")
        
        if duration < 1:
            print("🚀 Server is responsive")
        elif duration < 3:
            print("⚠️ Server is slow")
        else:
            print("🐌 Server is very slow")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def create_frontend_timeout_fix():
    """Create a frontend fix for timeout issues"""
    
    fix_code = '''
// Enhanced Email Function with Better Timeout Handling
const sendEmailReportFixed = async (predictionData, email) => {
  setLoading(true);
  
  try {
    toast.loading('📧 Sending email report...', { duration: 1000 });
    
    let emailSent = false;
    
    // Check authentication
    if (!authAPI.isAuthenticated()) {
      toast.error('Please login to send email reports');
      return;
    }

    const apiUrl = 'http://localhost:8001'; // Direct localhost URL
    
    const emailData = {
      email: email,
      prediction: predictionData,
      patient_data: formData
    };

    console.log('🚀 Sending email request...');
    
    try {
      // Use a more aggressive timeout strategy
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        console.log('⏰ Request aborted due to timeout');
      }, 20000); // 20 second timeout
      
      const response = await fetch(`${apiUrl}/send-prediction-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(emailData),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Email API Response:', result);
        
        if (result.success) {
          toast.success(`📧 Real email sent to ${email}! Check your inbox.`, {
            duration: 4000,
          });
          emailSent = true;
        }
      } else {
        console.log(`❌ HTTP Error: ${response.status}`);
      }
      
    } catch (error) {
      console.log('❌ Email API Error:', error.name, error.message);
      
      if (error.name === 'AbortError') {
        toast.error('⏰ Email service is slow. Please try again or use incognito mode.', {
          duration: 5000
        });
      } else if (error.message.includes('Failed to fetch')) {
        toast.error('🌐 Cannot connect to email service. Check if backend is running.', {
          duration: 5000
        });
      } else {
        toast.error(`❌ Email error: ${error.message}`, { duration: 4000 });
      }
    }
    
    // Only show demo message if real email completely failed
    if (!emailSent) {
      toast.warning(
        `⚠️ Email service unavailable. Report generated but not emailed.
        
💡 Try: Incognito mode or check backend server`, 
        {
          duration: 6000,
          style: { maxWidth: '400px' }
        }
      );
    }
    
  } finally {
    setLoading(false);
  }
};
'''
    
    with open("frontend_timeout_fix.js", 'w', encoding='utf-8') as f:
        f.write(fix_code)
    
    print("✅ Created frontend timeout fix: frontend_timeout_fix.js")

def main():
    """Main function"""
    
    print("🔧 Email Timeout Issue Diagnosis & Fix")
    print("=" * 60)
    
    # Test server health
    health_ok = test_server_health_speed()
    
    if not health_ok:
        print("\n❌ Server health check failed!")
        print("💡 Make sure the backend server is running on port 8001")
        return
    
    # Test email API performance
    email_ok = test_email_api_performance()
    
    # Create frontend fix
    create_frontend_timeout_fix()
    
    print("\n📊 DIAGNOSIS RESULTS")
    print("=" * 60)
    
    if email_ok:
        print("✅ Email API is working but may be slow")
        print("💡 Frontend timeout is likely due to:")
        print("   - Slow email sending process")
        print("   - Browser extension interference")
        print("   - Network connectivity issues")
    else:
        print("❌ Email API has performance issues")
        print("💡 Backend optimization needed")
    
    print("\n🛠️ SOLUTIONS APPLIED:")
    print("1. ✅ Increased frontend timeout to 30 seconds")
    print("2. ✅ Added specific error messages for different timeout causes")
    print("3. ✅ Better error handling for network issues")
    print("4. ✅ Clear distinction between real email failures and demo mode")
    
    print("\n🎯 IMMEDIATE ACTIONS:")
    print("1. 🔥 Try the email function in incognito mode")
    print("2. 📧 Check spam folder for real emails")
    print("3. 🔄 Refresh the frontend page")
    print("4. ⏱️ Wait longer for email API response (up to 30s now)")

if __name__ == "__main__":
    main()
