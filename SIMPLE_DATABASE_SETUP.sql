-- SIMPLE DATABASE SETUP FOR MEDICARE+ PLATFORM
-- Run this in Supabase SQL Editor to create tables and insert admin users
-- This will fix PGRST205 error and ensure data storage works

-- 1. Create users table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create datasets table  
CREATE TABLE IF NOT EXISTS public.datasets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    columns TEXT[] NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create dataset_rows table
CREATE TABLE IF NOT EXISTS public.dataset_rows (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    dataset_id UUID REFERENCES public.datasets(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create model_metadata table
CREATE TABLE IF NOT EXISTS public.model_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    training_samples INTEGER,
    test_samples INTEGER,
    train_rmse FLOAT,
    test_rmse FLOAT,
    train_r2 FLOAT,
    test_r2 FLOAT,
    features TEXT[],
    model_version VARCHAR(50) DEFAULT '1.0',
    dataset_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create predictions table
CREATE TABLE IF NOT EXISTS public.predictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    input_data JSONB NOT NULL,
    prediction FLOAT NOT NULL,
    confidence FLOAT DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_datasets_filename ON public.datasets(filename);
CREATE INDEX IF NOT EXISTS idx_predictions_user_email ON public.predictions(user_email);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON public.predictions(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for service role (full access)
DROP POLICY IF EXISTS "Service role can do everything on users" ON public.users;
CREATE POLICY "Service role can do everything on users" ON public.users
    FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role can do everything on datasets" ON public.datasets;
CREATE POLICY "Service role can do everything on datasets" ON public.datasets
    FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role can do everything on dataset_rows" ON public.dataset_rows;
CREATE POLICY "Service role can do everything on dataset_rows" ON public.dataset_rows
    FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role can do everything on model_metadata" ON public.model_metadata;
CREATE POLICY "Service role can do everything on model_metadata" ON public.model_metadata
    FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role can do everything on predictions" ON public.predictions;
CREATE POLICY "Service role can do everything on predictions" ON public.predictions
    FOR ALL USING (auth.role() = 'service_role');

-- Insert admin users (these will be visible in your database)
INSERT INTO public.users (email, password, is_admin, created_at) VALUES 
('admin@example.com', 'admin123', TRUE, NOW()),
('user@example.com', 'user123', FALSE, NOW()),
('demo@example.com', 'demo123', FALSE, NOW())
ON CONFLICT (email) DO UPDATE SET
    password = EXCLUDED.password,
    is_admin = EXCLUDED.is_admin,
    updated_at = NOW();

-- Insert sample dataset metadata
INSERT INTO public.datasets (filename, rows, columns, upload_date, metadata) VALUES 
('sample_medical_insurance_data.csv', 1000, ARRAY['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr', 'claim_amount_inr'], NOW(), '{"source": "sample", "description": "Initial sample dataset"}')
ON CONFLICT DO NOTHING;

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema';

-- Grant permissions
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, service_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Final verification - Check if users were created
SELECT 
    'ADMIN USERS CREATED:' as status,
    email,
    is_admin,
    created_at
FROM public.users 
WHERE is_admin = TRUE
ORDER BY created_at;

-- Show all users
SELECT 
    'ALL USERS:' as status,
    email,
    CASE WHEN is_admin THEN 'ADMIN' ELSE 'USER' END as role,
    created_at
FROM public.users 
ORDER BY is_admin DESC, created_at;
