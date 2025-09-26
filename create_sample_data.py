#!/usr/bin/env python3
"""
Create sample dataset if none exists
"""

import pandas as pd
import numpy as np
import os

def create_sample_dataset():
    """Create a sample dataset for testing"""
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Check if any CSV files exist
    csv_files = [f for f in os.listdir("data") if f.endswith('.csv')]
    
    if csv_files:
        print(f"Found existing dataset(s): {csv_files}")
        return
    
    print("No dataset found. Creating sample dataset...")
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'age': np.random.randint(18, 70, n_samples),
        'bmi': np.random.normal(25, 4, n_samples).round(1),
        'gender': np.random.choice(['Male', 'Female'], n_samples),
        'smoker': np.random.choice(['Yes', 'No'], n_samples, p=[0.2, 0.8]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_samples),
        'premium_annual_inr': np.random.randint(10000, 50000, n_samples)
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate claim amounts based on features (with some logic)
    base_claim = 5000
    age_factor = (df['age'] - 18) * 200
    bmi_factor = np.where(df['bmi'] > 30, (df['bmi'] - 30) * 500, 0)
    smoker_factor = np.where(df['smoker'] == 'Yes', 15000, 0)
    premium_factor = df['premium_annual_inr'] * 0.3
    
    df['claim_amount_inr'] = (
        base_claim + age_factor + bmi_factor + smoker_factor + premium_factor + 
        np.random.normal(0, 5000, n_samples)
    ).round(0).astype(int)
    
    # Ensure no negative claims
    df['claim_amount_inr'] = df['claim_amount_inr'].clip(lower=0)
    
    # Save to CSV
    output_path = "data/sample_medical_insurance_data.csv"
    df.to_csv(output_path, index=False)
    
    print(f"✅ Created sample dataset: {output_path}")
    print(f"📊 Dataset contains {len(df)} rows")
    print(f"💰 Average claim: ₹{df['claim_amount_inr'].mean():.2f}")
    print(f"💳 Average premium: ₹{df['premium_annual_inr'].mean():.2f}")

if __name__ == "__main__":
    create_sample_dataset()
