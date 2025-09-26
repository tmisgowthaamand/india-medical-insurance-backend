-- Simple MediCare+ Database Schema (No RLS for easier deployment)
-- Run this in your Supabase SQL Editor

-- 1. Users table
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Datasets table
CREATE TABLE IF NOT EXISTS public.datasets (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    columns TEXT NOT NULL, -- JSON string of column names
    upload_date TIMESTAMP DEFAULT NOW(),
    metadata TEXT DEFAULT '{}' -- JSON string
);

-- 3. Dataset rows table
CREATE TABLE IF NOT EXISTS public.dataset_rows (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES public.datasets(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    data TEXT NOT NULL -- JSON string of row data
);

-- 4. Model metadata table
CREATE TABLE IF NOT EXISTS public.model_metadata (
    id SERIAL PRIMARY KEY,
    training_date TIMESTAMP DEFAULT NOW(),
    training_samples INTEGER,
    test_samples INTEGER,
    train_rmse DECIMAL(10, 4),
    test_rmse DECIMAL(10, 4),
    train_r2 DECIMAL(10, 4),
    test_r2 DECIMAL(10, 4),
    features TEXT, -- JSON string of feature names
    model_version VARCHAR(50) DEFAULT '1.0',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Predictions table
CREATE TABLE IF NOT EXISTS public.predictions (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    input_data TEXT NOT NULL, -- JSON string
    prediction DECIMAL(12, 2) NOT NULL,
    confidence DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_predictions_user_email ON public.predictions(user_email);

-- Insert default admin user
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
    '["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"]',
    '1.0',
    'active'
);

SELECT 'Database tables created successfully!' as result;
