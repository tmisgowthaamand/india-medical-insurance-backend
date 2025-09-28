-- SIMPLE SUPABASE FIX for PGRST205 Error
-- Copy and paste this ENTIRE script into Supabase SQL Editor and click RUN
-- This will fix: "Could not find the table 'public.users' in the schema cache"

-- Step 1: Clean slate (remove existing tables if any)
DROP TABLE IF EXISTS public.predictions CASCADE;
DROP TABLE IF EXISTS public.dataset_rows CASCADE;
DROP TABLE IF EXISTS public.model_metadata CASCADE;
DROP TABLE IF EXISTS public.datasets CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- Step 2: Create Users table (MOST IMPORTANT for fixing PGRST205)
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create supporting tables
CREATE TABLE public.datasets (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    columns TEXT NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata TEXT DEFAULT '{}'
);

CREATE TABLE public.dataset_rows (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES public.datasets(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    data TEXT NOT NULL
);

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

CREATE TABLE public.predictions (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    input_data TEXT NOT NULL,
    prediction DECIMAL(12, 2) NOT NULL,
    confidence DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 4: Create indexes for performance
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_predictions_user_email ON public.predictions(user_email);
CREATE INDEX idx_predictions_created_at ON public.predictions(created_at);
CREATE INDEX idx_datasets_upload_date ON public.datasets(upload_date);
CREATE INDEX idx_dataset_rows_dataset_id ON public.dataset_rows(dataset_id);

-- Step 5: Insert default admin user
INSERT INTO public.users (email, password, is_admin, created_at) 
VALUES ('admin@medicare.com', 'admin123', true, NOW())
ON CONFLICT (email) DO NOTHING;

-- Step 6: Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

-- Step 7: Create policies for service role access
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

-- Step 8: CRITICAL - Refresh PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Step 9: Verify tables were created
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN ('users', 'datasets', 'dataset_rows', 'model_metadata', 'predictions')
ORDER BY tablename;

-- SUCCESS MESSAGE
-- If you see 5 rows returned above, your PGRST205 error is FIXED!
-- Now restart your Render service: srv-d3b668ogjchc73f9ece0
