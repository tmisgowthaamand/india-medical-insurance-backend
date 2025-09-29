-- PGRST205 Complete Fix: Create all required database tables
-- This script creates all necessary tables for the MediCare+ platform
-- Run this in your Supabase SQL Editor to fix the PGRST205 error

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS public.predictions CASCADE;
DROP TABLE IF EXISTS public.model_metadata CASCADE;
DROP TABLE IF EXISTS public.dataset_rows CASCADE;
DROP TABLE IF EXISTS public.datasets CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- 1. Create users table
CREATE TABLE public.users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create datasets table
CREATE TABLE public.datasets (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    columns TEXT[] NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create dataset_rows table
CREATE TABLE public.dataset_rows (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    dataset_id UUID REFERENCES public.datasets(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create model_metadata table
CREATE TABLE public.model_metadata (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    training_samples INTEGER,
    test_samples INTEGER,
    train_rmse FLOAT,
    test_rmse FLOAT,
    train_r2 FLOAT,
    test_r2 FLOAT,
    features TEXT[],
    model_version VARCHAR(50) DEFAULT '1.0',
    dataset_id UUID REFERENCES public.datasets(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create predictions table
CREATE TABLE public.predictions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    input_data JSONB NOT NULL,
    prediction FLOAT NOT NULL,
    confidence FLOAT DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_datasets_filename ON public.datasets(filename);
CREATE INDEX idx_datasets_upload_date ON public.datasets(upload_date DESC);
CREATE INDEX idx_dataset_rows_dataset_id ON public.dataset_rows(dataset_id);
CREATE INDEX idx_dataset_rows_row_index ON public.dataset_rows(dataset_id, row_index);
CREATE INDEX idx_model_metadata_training_date ON public.model_metadata(training_date DESC);
CREATE INDEX idx_predictions_user_email ON public.predictions(user_email);
CREATE INDEX idx_predictions_created_at ON public.predictions(created_at DESC);

-- Enable Row Level Security (RLS) for all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for service role (full access)
CREATE POLICY "Service role can do everything on users" ON public.users
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can do everything on datasets" ON public.datasets
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can do everything on dataset_rows" ON public.dataset_rows
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can do everything on model_metadata" ON public.model_metadata
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can do everything on predictions" ON public.predictions
    FOR ALL USING (auth.role() = 'service_role');

-- Create RLS policies for authenticated users
CREATE POLICY "Users can read their own data" ON public.users
    FOR SELECT USING (auth.uid()::text = id::text OR auth.role() = 'authenticated');

CREATE POLICY "Users can read datasets" ON public.datasets
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read dataset_rows" ON public.dataset_rows
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read model_metadata" ON public.model_metadata
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read their own predictions" ON public.predictions
    FOR SELECT USING (auth.role() = 'authenticated');

-- Insert default admin user
INSERT INTO public.users (email, password, is_admin, created_at) VALUES 
('admin@example.com', 'admin123', TRUE, NOW()),
('user@example.com', 'user123', FALSE, NOW()),
('demo@example.com', 'demo123', FALSE, NOW())
ON CONFLICT (email) DO NOTHING;

-- Insert sample dataset metadata (optional)
INSERT INTO public.datasets (filename, rows, columns, upload_date, metadata) VALUES 
('sample_medical_insurance_data.csv', 1000, ARRAY['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr', 'claim_amount_inr'], NOW(), '{"source": "sample", "description": "Initial sample dataset"}')
ON CONFLICT DO NOTHING;

-- Insert sample model metadata (optional)
INSERT INTO public.model_metadata (training_samples, test_samples, train_rmse, test_rmse, train_r2, test_r2, features, model_version) VALUES 
(800, 200, 5000.0, 5200.0, 0.85, 0.82, ARRAY['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr'], '1.0')
ON CONFLICT DO NOTHING;

-- Refresh the schema cache to make tables immediately available
NOTIFY pgrst, 'reload schema';

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, service_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Final schema cache refresh
NOTIFY pgrst, 'reload schema';

-- Verification queries (run these to confirm setup)
-- SELECT 'users' as table_name, count(*) as row_count FROM public.users
-- UNION ALL
-- SELECT 'datasets' as table_name, count(*) as row_count FROM public.datasets
-- UNION ALL
-- SELECT 'dataset_rows' as table_name, count(*) as row_count FROM public.dataset_rows
-- UNION ALL
-- SELECT 'model_metadata' as table_name, count(*) as row_count FROM public.model_metadata
-- UNION ALL
-- SELECT 'predictions' as table_name, count(*) as row_count FROM public.predictions;
