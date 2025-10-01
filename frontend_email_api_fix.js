
// Enhanced Email API Integration - No Browser Extension Conflicts
// Add this to your frontend to ensure real emails are sent

const sendRealEmail = async (emailData) => {
  console.log('🚀 Attempting to send REAL email via API...');
  
  try {
    // Use axios instead of fetch to avoid some browser extension conflicts
    const response = await fetch('http://localhost:8001/send-prediction-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Cache-Control': 'no-cache'
      },
      body: JSON.stringify(emailData),
      mode: 'cors',
      credentials: 'omit'
    });

    console.log('📊 Response status:', response.status);
    
    if (response.ok) {
      const result = await response.json();
      console.log('📧 Email API result:', result);
      
      if (result.success) {
        console.log('✅ REAL EMAIL SENT SUCCESSFULLY!');
        return { success: true, message: result.message, real: true };
      } else {
        console.log('❌ Email API returned failure:', result.message);
        return { success: false, message: result.message, real: false };
      }
    } else {
      console.log('❌ HTTP error:', response.status);
      const errorText = await response.text();
      console.log('Error details:', errorText);
      return { success: false, message: `HTTP ${response.status}`, real: false };
    }
  } catch (error) {
    console.log('❌ Email API request failed:', error);
    return { success: false, message: error.message, real: false };
  }
};

// Usage example:
/*
const emailData = {
  email: "user@example.com",
  prediction: { prediction: 25000, confidence: 0.85 },
  patient_data: { age: 35, bmi: 23.0, gender: "Male", smoker: "No", region: "East", premium_annual_inr: 25000 }
};

sendRealEmail(emailData).then(result => {
  if (result.success && result.real) {
    toast.success(`📧 Real email sent to ${emailData.email}! Check your inbox.`);
  } else if (result.success) {
    toast.warning(`📧 Demo email sent (backend issue): ${result.message}`);
  } else {
    toast.error(`❌ Email failed: ${result.message}`);
  }
});
*/
