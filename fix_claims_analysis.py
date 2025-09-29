#!/usr/bin/env python3
"""
Fix Claims Analysis Data Structure
This script fixes the region analysis data structure to match frontend expectations
"""

import pandas as pd
import os
import json

def test_fixed_claims_analysis():
    """Test the fixed claims analysis function"""
    # Find dataset
    dataset_to_use = None
    
    # First try the current CSV_PATH
    csv_path = "data/sample_medical_insurance_data.csv"
    if os.path.exists(csv_path):
        dataset_to_use = csv_path
    else:
        # Look for any CSV file in data directory
        data_dir = "data"
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            if csv_files:
                dataset_to_use = os.path.join(data_dir, csv_files[0])
    
    if not dataset_to_use:
        print("❌ No dataset found")
        return None
    
    print(f"📊 Using dataset: {dataset_to_use}")
    
    try:
        df = pd.read_csv(dataset_to_use)
        
        # Age group analysis
        df['age_group'] = pd.cut(df['age'], bins=[0, 30, 40, 50, 60, 100], labels=['<30', '30-40', '40-50', '50-60', '60+'])
        age_groups = df.groupby('age_group').agg({
            'claim_amount_inr': 'mean',
            'premium_annual_inr': 'mean'
        }).to_dict()
        
        # Region analysis - FIXED VERSION
        region_stats = df.groupby('region').agg({
            'claim_amount_inr': ['mean', 'count'],
            'premium_annual_inr': 'mean'
        })
        
        # Restructure region analysis to match frontend expectations
        region_analysis = {
            'claim_amount_inr': {
                'mean': region_stats[('claim_amount_inr', 'mean')].to_dict(),
                'count': region_stats[('claim_amount_inr', 'count')].to_dict()
            },
            'premium_annual_inr': region_stats[('premium_annual_inr', 'mean')].to_dict()
        }
        
        # Smoker analysis
        smoker_analysis = df.groupby('smoker').agg({
            'claim_amount_inr': 'mean',
            'premium_annual_inr': 'mean'
        }).to_dict()
        
        # Premium vs Claims correlation
        premium_bins = pd.qcut(df['premium_annual_inr'], q=5, labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])
        premium_vs_claims = df.groupby(premium_bins)['claim_amount_inr'].mean().to_dict()
        
        result = {
            'age_groups': age_groups,
            'region_analysis': region_analysis,
            'smoker_analysis': smoker_analysis,
            'premium_vs_claims': premium_vs_claims
        }
        
        print("✅ Fixed claims analysis structure:")
        print("📈 Age groups:", len(age_groups['claim_amount_inr']), "groups")
        print("🗺️ Regions:", len(region_analysis['claim_amount_inr']['mean']), "regions")
        print("🚬 Smoker analysis:", len(smoker_analysis['claim_amount_inr']), "categories")
        print("💰 Premium bands:", len(premium_vs_claims), "bands")
        
        # Test frontend data access patterns
        print("\n🧪 Testing frontend data access patterns:")
        
        # Test region data access (this is what was failing)
        try:
            region_means = region_analysis['claim_amount_inr']['mean']
            region_counts = region_analysis['claim_amount_inr']['count']
            print("✅ Region means accessible:", list(region_means.keys()))
            print("✅ Region counts accessible:", list(region_counts.keys()))
        except Exception as e:
            print(f"❌ Region data access failed: {e}")
        
        # Test chart data preparation (like frontend does)
        try:
            regionData = []
            for region in region_analysis['claim_amount_inr']['mean'].keys():
                regionData.append({
                    'region': region,
                    'avgClaim': region_analysis['claim_amount_inr']['mean'][region],
                    'count': region_analysis['claim_amount_inr']['count'][region],
                    'avgPremium': region_analysis['premium_annual_inr'][region]
                })
            print("✅ Chart data prepared successfully:", len(regionData), "regions")
            for item in regionData:
                print(f"   - {item['region']}: ₹{item['avgClaim']:.0f} avg claim, {item['count']} policies")
        except Exception as e:
            print(f"❌ Chart data preparation failed: {e}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in claims analysis: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Testing Fixed Claims Analysis Data Structure")
    print("=" * 60)
    result = test_fixed_claims_analysis()
    if result:
        print("\n🎉 Claims analysis fix successful!")
        print("📋 Next: Apply this fix to the main app.py file")
    else:
        print("\n❌ Claims analysis fix failed!")
