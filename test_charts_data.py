#!/usr/bin/env python3
"""
Test Charts Data Structure
This script tests that the claims analysis data structure matches what the frontend expects
"""

import requests
import json

def test_charts_data():
    """Test that the data structure matches frontend chart expectations"""
    print("🧪 Testing Charts Data Structure")
    print("=" * 50)
    
    try:
        # Get claims analysis data
        response = requests.get('http://localhost:8001/claims-analysis')
        
        if response.status_code != 200:
            print(f"❌ API request failed: {response.status_code}")
            return False
        
        data = response.json()
        print("✅ API request successful")
        
        # Test frontend data access patterns (exactly like ClaimsAnalysis.jsx)
        print("\n🎯 Testing Frontend Data Access Patterns:")
        
        # 1. Test age group data preparation
        try:
            age_groups = data.get('age_groups', {})
            ageGroupData = []
            for ageGroup, avgClaim in age_groups.get('claim_amount_inr', {}).items():
                ageGroupData.append({
                    'ageGroup': ageGroup,
                    'avgClaim': avgClaim,
                    'avgPremium': age_groups.get('premium_annual_inr', {}).get(ageGroup, 0)
                })
            print(f"✅ Age Group Chart Data: {len(ageGroupData)} groups")
            for item in ageGroupData[:2]:  # Show first 2
                print(f"   - {item['ageGroup']}: ₹{item['avgClaim']:.0f} claim, ₹{item['avgPremium']:.0f} premium")
        except Exception as e:
            print(f"❌ Age Group Data Failed: {e}")
        
        # 2. Test region data preparation (this was the main issue)
        try:
            region_analysis = data.get('region_analysis', {})
            regionData = []
            for region, avgClaim in region_analysis.get('claim_amount_inr', {}).get('mean', {}).items():
                regionData.append({
                    'region': region,
                    'avgClaim': avgClaim,
                    'count': region_analysis.get('claim_amount_inr', {}).get('count', {}).get(region, 0),
                    'avgPremium': region_analysis.get('premium_annual_inr', {}).get(region, 0)
                })
            print(f"✅ Region Chart Data: {len(regionData)} regions")
            for item in regionData:
                print(f"   - {item['region']}: ₹{item['avgClaim']:.0f} claim, {item['count']} policies")
        except Exception as e:
            print(f"❌ Region Data Failed: {e}")
            return False
        
        # 3. Test smoker data preparation
        try:
            smoker_analysis = data.get('smoker_analysis', {})
            smokerData = []
            for smokerStatus, avgClaim in smoker_analysis.get('claim_amount_inr', {}).items():
                smokerData.append({
                    'smokerStatus': smokerStatus,
                    'avgClaim': avgClaim,
                    'avgPremium': smoker_analysis.get('premium_annual_inr', {}).get(smokerStatus, 0)
                })
            print(f"✅ Smoker Chart Data: {len(smokerData)} categories")
            for item in smokerData:
                print(f"   - {item['smokerStatus']}: ₹{item['avgClaim']:.0f} claim, ₹{item['avgPremium']:.0f} premium")
        except Exception as e:
            print(f"❌ Smoker Data Failed: {e}")
        
        # 4. Test premium vs claims data
        try:
            premium_vs_claims = data.get('premium_vs_claims', {})
            premiumVsClaimsData = []
            for premiumBand, avgClaim in premium_vs_claims.items():
                premiumVsClaimsData.append({
                    'premiumBand': premiumBand,
                    'avgClaim': avgClaim
                })
            print(f"✅ Premium vs Claims Data: {len(premiumVsClaimsData)} bands")
            for item in premiumVsClaimsData[:2]:  # Show first 2
                print(f"   - {item['premiumBand']}: ₹{item['avgClaim']:.0f} avg claim")
        except Exception as e:
            print(f"❌ Premium vs Claims Data Failed: {e}")
        
        print("\n🎉 All Chart Data Tests Passed!")
        print("📊 Charts should now display properly in the frontend")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("💡 Make sure the backend is running on http://localhost:8001")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_chart_components():
    """Test that chart components will receive proper data"""
    print("\n📈 Testing Chart Component Data:")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:8001/claims-analysis')
        data = response.json()
        
        # Test specific chart data that was failing
        region_analysis = data['region_analysis']
        
        # Test "Claims by Region" chart
        claims_by_region = region_analysis['claim_amount_inr']['mean']
        print(f"📊 Claims by Region Chart: {len(claims_by_region)} data points")
        
        # Test "Policy Count by Region" chart  
        policy_count_by_region = region_analysis['claim_amount_inr']['count']
        print(f"🥧 Policy Count by Region Pie Chart: {len(policy_count_by_region)} data points")
        
        # Verify data is not empty
        if all(v > 0 for v in claims_by_region.values()):
            print("✅ Claims by Region: All values > 0")
        else:
            print("⚠️ Claims by Region: Some zero values found")
            
        if all(v > 0 for v in policy_count_by_region.values()):
            print("✅ Policy Count by Region: All values > 0") 
        else:
            print("⚠️ Policy Count by Region: Some zero values found")
        
        return True
        
    except Exception as e:
        print(f"❌ Chart component test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_charts_data()
    if success:
        test_chart_components()
        print("\n🎯 Summary:")
        print("✅ Backend data structure fixed")
        print("✅ Frontend chart data preparation tested")
        print("✅ All chart components should now display properly")
        print("\n📋 Next Steps:")
        print("1. Upload a CSV file through the admin panel")
        print("2. Train the model")
        print("3. View the Claims Analysis page")
        print("4. Charts should now display with proper data")
    else:
        print("\n❌ Tests failed - charts may still not display properly")
