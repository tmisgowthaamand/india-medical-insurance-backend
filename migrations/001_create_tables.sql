-- MediCare+ Database Schema Migration
-- This script creates all the necessary tables for the medical insurance dashboard

-- Enable UUID extension for better ID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users table for authentication and user management
CREATE TABLE IF NOT EXISTS public.users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Datasets table for storing dataset metadata
CREATE TABLE IF NOT EXISTS public.datasets (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    columns TEXT[] NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Dataset rows table for storing actual dataset data
CREATE TABLE IF NOT EXISTS public.dataset_rows (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    dataset_id UUID REFERENCES public.datasets(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Model metadata table for ML model information
CREATE TABLE IF NOT EXISTS public.model_metadata (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    training_samples INTEGER,
    test_samples INTEGER,
    train_rmse DECIMAL(10, 4),
    test_rmse DECIMAL(10, 4),
    train_r2 DECIMAL(10, 4),
    test_r2 DECIMAL(10, 4),
    features TEXT[],
    model_version VARCHAR(50) DEFAULT '1.0',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Predictions table for storing prediction results
CREATE TABLE IF NOT EXISTS public.predictions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    input_data JSONB NOT NULL,
    prediction DECIMAL(12, 2) NOT NULL,
    confidence DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_datasets_filename ON public.datasets(filename);
CREATE INDEX IF NOT EXISTS idx_datasets_upload_date ON public.datasets(upload_date DESC);
CREATE INDEX IF NOT EXISTS idx_dataset_rows_dataset_id ON public.dataset_rows(dataset_id);
CREATE INDEX IF NOT EXISTS idx_model_metadata_created_at ON public.model_metadata(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_user_email ON public.predictions(user_email);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON public.predictions(created_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at trigger to users table
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password should be hashed in production)
INSERT INTO public.users (email, password, is_admin) 
VALUES ('admin@medicare.com', 'admin123', TRUE)
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
    ARRAY['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr'],
    '1.0',
    'active'
) ON CONFLICT DO NOTHING;

-- Grant necessary permissions (adjust based on your Supabase setup)
-- These might need to be run separately in Supabase SQL editor with proper roles

-- Enable Row Level Security (RLS) for better security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
-- Note: Adjust these policies based on your security requirements

-- Users can read their own data, admins can read all
CREATE POLICY "Users can view own data" ON public.users
    FOR SELECT USING (auth.email() = email OR 
                     EXISTS (SELECT 1 FROM public.users WHERE email = auth.email() AND is_admin = TRUE));

-- Users can update their own data, admins can update all
CREATE POLICY "Users can update own data" ON public.users
    FOR UPDATE USING (auth.email() = email OR 
                     EXISTS (SELECT 1 FROM public.users WHERE email = auth.email() AND is_admin = TRUE));

-- Only admins can insert new users
CREATE POLICY "Only admins can create users" ON public.users
    FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM public.users WHERE email = auth.email() AND is_admin = TRUE));

-- Datasets: Authenticated users can read, admins can modify
CREATE POLICY "Authenticated users can view datasets" ON public.datasets
    FOR SELECT TO authenticated USING (TRUE);

CREATE POLICY "Only admins can modify datasets" ON public.datasets
    FOR ALL TO authenticated USING (EXISTS (SELECT 1 FROM public.users WHERE email = auth.email() AND is_admin = TRUE));

-- Dataset rows: Same as datasets
CREATE POLICY "Authenticated users can view dataset rows" ON public.dataset_rows
    FOR SELECT TO authenticated USING (TRUE);

CREATE POLICY "Only admins can modify dataset rows" ON public.dataset_rows
    FOR ALL TO authenticated USING (EXISTS (SELECT 1 FROM public.users WHERE email = auth.email() AND is_admin = TRUE));

-- Model metadata: Authenticated users can read, admins can modify
CREATE POLICY "Authenticated users can view model metadata" ON public.model_metadata
    FOR SELECT TO authenticated USING (TRUE);

CREATE POLICY "Only admins can modify model metadata" ON public.model_metadata
    FOR ALL TO authenticated USING (EXISTS (SELECT 1 FROM public.users WHERE email = auth.email() AND is_admin = TRUE));

-- Predictions: Users can view their own, admins can view all
CREATE POLICY "Users can view own predictions" ON public.predictions
    FOR SELECT USING (user_email = auth.email() OR 
                     EXISTS (SELECT 1 FROM public.users WHERE email = auth.email() AND is_admin = TRUE));

CREATE POLICY "Authenticated users can create predictions" ON public.predictions
    FOR INSERT TO authenticated WITH CHECK (user_email = auth.email());

-- Comments for documentation
COMMENT ON TABLE public.users IS 'User accounts for authentication and authorization';
COMMENT ON TABLE public.datasets IS 'Metadata for uploaded medical insurance datasets';
COMMENT ON TABLE public.dataset_rows IS 'Actual data rows from uploaded datasets';
COMMENT ON TABLE public.model_metadata IS 'Machine learning model training information and metrics';
COMMENT ON TABLE public.predictions IS 'AI prediction results for insurance claims';

-- Success message
SELECT 'MediCare+ database schema created successfully!' as message;
