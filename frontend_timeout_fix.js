
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
