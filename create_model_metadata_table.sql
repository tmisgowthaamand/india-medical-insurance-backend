-- Create or update model_metadata table with correct structure
-- Run this in your Supabase SQL editor

-- Drop existing table if it exists (be careful with this in production!)
DROP TABLE IF EXISTS public.model_metadata CASCADE;

-- Create model_metadata table with all required columns
CREATE TABLE public.model_metadata (
    id BIGSERIAL PRIMARY KEY,
    model_type TEXT NOT NULL DEFAULT 'RandomForestRegressor',
    training_dataset TEXT NOT NULL,
    training_samples INTEGER NOT NULL DEFAULT 0,
    test_r2_score FLOAT NOT NULL DEFAULT 0.0,
    test_rmse FLOAT NOT NULL DEFAULT 0.0,
    features TEXT[] DEFAULT '{}',
    trained_by TEXT NOT NULL,
    training_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'active',
    training_type TEXT DEFAULT 'manual',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_model_metadata_training_date ON public.model_metadata(training_date DESC);
CREATE INDEX idx_model_metadata_status ON public.model_metadata(status);
CREATE INDEX idx_model_metadata_trained_by ON public.model_metadata(trained_by);

-- Enable Row Level Security (RLS)
ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;

-- Create policies for RLS
-- Allow authenticated users to read all model metadata
CREATE POLICY "Allow authenticated users to read model metadata" ON public.model_metadata
    FOR SELECT USING (auth.role() = 'authenticated');

-- Allow service role to do everything (for backend operations)
CREATE POLICY "Allow service role full access to model metadata" ON public.model_metadata
    FOR ALL USING (auth.role() = 'service_role');

-- Allow authenticated users to insert their own model metadata
CREATE POLICY "Allow authenticated users to insert model metadata" ON public.model_metadata
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Grant necessary permissions
GRANT ALL ON public.model_metadata TO authenticated;
GRANT ALL ON public.model_metadata TO service_role;
GRANT USAGE, SELECT ON SEQUENCE model_metadata_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE model_metadata_id_seq TO service_role;

-- Insert sample data
INSERT INTO public.model_metadata (
    model_type,
    training_dataset,
    training_samples,
    test_r2_score,
    test_rmse,
    features,
    trained_by,
    training_date,
    status,
    training_type
) VALUES 
(
    'RandomForestRegressor',
    'india_medical_insurance_2025_synthetic.csv',
    1250,
    0.92,
    3500.0,
    ARRAY['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr'],
    'admin@example.com',
    NOW() - INTERVAL '2 days',
    'active',
    'initial'
),
(
    'RandomForestRegressor',
    'medical_insurance_updated_2025.csv',
    980,
    0.89,
    4200.0,
    ARRAY['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr'],
    'admin@gmail.com',
    NOW() - INTERVAL '1 day',
    'active',
    'retrain'
),
(
    'RandomForestRegressor',
    'insurance_claims_data_2025.csv',
    1500,
    0.94,
    3200.0,
    ARRAY['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr'],
    'admin@example.com',
    NOW(),
    'active',
    'upload'
);

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema';

-- Verify the table was created correctly
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'model_metadata'
ORDER BY ordinal_position;
