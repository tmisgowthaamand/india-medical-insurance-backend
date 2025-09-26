-- Supabase Database Schema for India Medical Insurance Dashboard
-- Run these commands in your Supabase SQL editor

-- Enable Row Level Security (RLS)
-- You can customize these policies based on your security requirements

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 2. Datasets table
CREATE TABLE IF NOT EXISTS datasets (
    id BIGSERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    columns JSONB NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    uploaded_by VARCHAR(255) REFERENCES users(email),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster filename and date lookups
CREATE INDEX IF NOT EXISTS idx_datasets_filename ON datasets(filename);
CREATE INDEX IF NOT EXISTS idx_datasets_upload_date ON datasets(upload_date DESC);

-- 3. Dataset rows table (for storing actual data)
CREATE TABLE IF NOT EXISTS dataset_rows (
    id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT REFERENCES datasets(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster data retrieval
CREATE INDEX IF NOT EXISTS idx_dataset_rows_dataset_id ON dataset_rows(dataset_id);
CREATE INDEX IF NOT EXISTS idx_dataset_rows_dataset_row ON dataset_rows(dataset_id, row_index);

-- 4. Model metadata table
CREATE TABLE IF NOT EXISTS model_metadata (
    id BIGSERIAL PRIMARY KEY,
    training_date TIMESTAMP WITH TIME ZONE,
    training_samples INTEGER,
    test_samples INTEGER,
    train_rmse DECIMAL(10, 2),
    test_rmse DECIMAL(10, 2),
    train_r2 DECIMAL(5, 4),
    test_r2 DECIMAL(5, 4),
    features JSONB,
    dataset_id BIGINT REFERENCES datasets(id),
    model_version VARCHAR(50),
    additional_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster model metadata lookups
CREATE INDEX IF NOT EXISTS idx_model_metadata_created_at ON model_metadata(created_at DESC);

-- 5. Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    input_data JSONB NOT NULL,
    prediction DECIMAL(10, 2) NOT NULL,
    confidence DECIMAL(5, 4),
    model_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster prediction lookups
CREATE INDEX IF NOT EXISTS idx_predictions_user_email ON predictions(user_email);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_user_date ON predictions(user_email, created_at DESC);

-- 6. Application logs table (optional, for debugging)
CREATE TABLE IF NOT EXISTS app_logs (
    id BIGSERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    user_email VARCHAR(255),
    endpoint VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    additional_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster log lookups
CREATE INDEX IF NOT EXISTS idx_app_logs_created_at ON app_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_app_logs_level ON app_logs(level);

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE dataset_rows ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_logs ENABLE ROW LEVEL SECURITY;

-- Users table policies
-- Users can read their own data, admins can read all
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.jwt() ->> 'email' = email OR (auth.jwt() ->> 'is_admin')::boolean = true);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.jwt() ->> 'email' = email);

-- Datasets table policies
-- All authenticated users can read datasets, only admins can insert/update/delete
CREATE POLICY "Authenticated users can view datasets" ON datasets
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Admins can manage datasets" ON datasets
    FOR ALL TO authenticated USING ((auth.jwt() ->> 'is_admin')::boolean = true);

-- Dataset rows policies
-- All authenticated users can read dataset rows, only admins can insert/update/delete
CREATE POLICY "Authenticated users can view dataset rows" ON dataset_rows
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Admins can manage dataset rows" ON dataset_rows
    FOR ALL TO authenticated USING ((auth.jwt() ->> 'is_admin')::boolean = true);

-- Model metadata policies
-- All authenticated users can read model metadata, only admins can insert/update/delete
CREATE POLICY "Authenticated users can view model metadata" ON model_metadata
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Admins can manage model metadata" ON model_metadata
    FOR ALL TO authenticated USING ((auth.jwt() ->> 'is_admin')::boolean = true);

-- Predictions table policies
-- Users can view their own predictions, admins can view all
CREATE POLICY "Users can view own predictions" ON predictions
    FOR SELECT USING (auth.jwt() ->> 'email' = user_email OR (auth.jwt() ->> 'is_admin')::boolean = true);

CREATE POLICY "Authenticated users can insert predictions" ON predictions
    FOR INSERT TO authenticated WITH CHECK (auth.jwt() ->> 'email' = user_email);

-- App logs policies
-- Only admins can view logs
CREATE POLICY "Admins can view logs" ON app_logs
    FOR SELECT TO authenticated USING ((auth.jwt() ->> 'is_admin')::boolean = true);

CREATE POLICY "System can insert logs" ON app_logs
    FOR INSERT TO authenticated WITH CHECK (true);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (optional)
-- Replace with your actual admin credentials
INSERT INTO users (email, password, is_admin) 
VALUES ('admin@example.com', 'admin123', true)
ON CONFLICT (email) DO NOTHING;

-- Insert default regular user (optional)
INSERT INTO users (email, password, is_admin) 
VALUES ('user@example.com', 'user123', false)
ON CONFLICT (email) DO NOTHING;

-- Create a view for dataset statistics
CREATE OR REPLACE VIEW dataset_stats AS
SELECT 
    d.id,
    d.filename,
    d.rows,
    d.upload_date,
    d.uploaded_by,
    COUNT(dr.id) as actual_rows,
    CASE 
        WHEN COUNT(dr.id) = d.rows THEN 'Complete'
        WHEN COUNT(dr.id) > 0 THEN 'Partial'
        ELSE 'Empty'
    END as status
FROM datasets d
LEFT JOIN dataset_rows dr ON d.id = dr.dataset_id
GROUP BY d.id, d.filename, d.rows, d.upload_date, d.uploaded_by
ORDER BY d.upload_date DESC;

-- Create a view for user prediction statistics
CREATE OR REPLACE VIEW user_prediction_stats AS
SELECT 
    user_email,
    COUNT(*) as total_predictions,
    AVG(prediction) as avg_prediction,
    MIN(prediction) as min_prediction,
    MAX(prediction) as max_prediction,
    AVG(confidence) as avg_confidence,
    MAX(created_at) as last_prediction_date
FROM predictions
GROUP BY user_email
ORDER BY total_predictions DESC;
