-- MediCare+ Database Migration Script
-- Run this in Supabase SQL Editor to create all required tables
-- This fixes the PGRST205 error: "Could not find the table 'public.users' in the schema cache"

-- Drop existing tables if they exist (for clean migration)
DROP TABLE IF EXISTS public.predictions CASCADE;
DROP TABLE IF EXISTS public.dataset_rows CASCADE;
DROP TABLE IF EXISTS public.model_metadata CASCADE;
DROP TABLE IF EXISTS public.datasets CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- Create Users table
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Datasets table
CREATE TABLE public.datasets (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    columns TEXT NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata TEXT DEFAULT '{}'
);

-- Create Dataset rows table
CREATE TABLE public.dataset_rows (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES public.datasets(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    data TEXT NOT NULL
);

-- Create Model metadata table
CREATE TABLE public.model_metadata (
    id SERIAL PRIMARY KEY,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    training_samples INTEGER,
    test_samples INTEGER,
    train_rmse DECIMAL(10, 4),
    test_rmse DECIMAL(10, 4),
    train_r2 DECIMAL(10, 4),
    test_r2 DECIMAL(10, 4),
    features TEXT,
    model_version VARCHAR(50) DEFAULT '1.0',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Predictions table
CREATE TABLE public.predictions (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    input_data TEXT NOT NULL,
    prediction DECIMAL(12, 2) NOT NULL,
    confidence DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_predictions_user_email ON public.predictions(user_email);
CREATE INDEX idx_predictions_created_at ON public.predictions(created_at);
CREATE INDEX idx_datasets_upload_date ON public.datasets(upload_date);
CREATE INDEX idx_dataset_rows_dataset_id ON public.dataset_rows(dataset_id);

-- Insert default admin user
INSERT INTO public.users (email, password, is_admin, created_at) 
VALUES ('admin@medicare.com', 'admin123', true, NOW())
ON CONFLICT (email) DO NOTHING;

-- Insert sample model metadata
INSERT INTO public.model_metadata (
    training_samples, 
    test_samples, 
    train_rmse, 
    test_rmse, 
    train_r2, 
    test_r2, 
    features, 
    model_version, 
    status
) VALUES (
    1000, 
    250, 
    5000.50, 
    5200.75, 
    0.85, 
    0.82, 
    '["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"]', 
    '1.0', 
    'active'
) ON CONFLICT DO NOTHING;

-- Enable Row Level Security (RLS) for better security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

-- Create policies for service role access (allows backend to access all data)
CREATE POLICY "Service role can access all users" ON public.users
    FOR ALL USING (true);

CREATE POLICY "Service role can access all datasets" ON public.datasets
    FOR ALL USING (true);

CREATE POLICY "Service role can access all dataset_rows" ON public.dataset_rows
    FOR ALL USING (true);

CREATE POLICY "Service role can access all model_metadata" ON public.model_metadata
    FOR ALL USING (true);

CREATE POLICY "Service role can access all predictions" ON public.predictions
    FOR ALL USING (true);

-- Refresh the PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Verify tables were created successfully
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN ('users', 'datasets', 'dataset_rows', 'model_metadata', 'predictions')
ORDER BY tablename;
