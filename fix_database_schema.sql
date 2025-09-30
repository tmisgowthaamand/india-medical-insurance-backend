-- Fix Database Schema Issues
-- Add missing columns and tables for email functionality

-- 1. Add email_only column to users table (if it doesn't exist)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'email_only') THEN
        ALTER TABLE users ADD COLUMN email_only TEXT;
        COMMENT ON COLUMN users.email_only IS 'Email address for users who only provided email (no full signup)';
    END IF;
END $$;

-- 2. Create email_reports table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS email_reports (
    id BIGSERIAL PRIMARY KEY,
    recipient_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    prediction_data JSONB,
    patient_data JSONB,
    email_content JSONB,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'sent',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_email_reports_recipient ON email_reports(recipient_email);
CREATE INDEX IF NOT EXISTS idx_email_reports_sent_at ON email_reports(sent_at);
CREATE INDEX IF NOT EXISTS idx_users_email_only ON users(email_only);

-- 4. Add RLS policies for email_reports table
ALTER TABLE email_reports ENABLE ROW LEVEL SECURITY;

-- Policy to allow service role to do everything
CREATE POLICY IF NOT EXISTS "Service role can manage email_reports" ON email_reports
    FOR ALL USING (auth.role() = 'service_role');

-- Policy to allow authenticated users to view their own email reports
CREATE POLICY IF NOT EXISTS "Users can view their own email reports" ON email_reports
    FOR SELECT USING (recipient_email = auth.email());

-- 5. Grant necessary permissions
GRANT ALL ON email_reports TO service_role;
GRANT USAGE, SELECT ON SEQUENCE email_reports_id_seq TO service_role;

-- 6. Update users table permissions for email_only column
GRANT UPDATE ON users TO service_role;

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';

-- Verification queries
SELECT 'email_only column exists' as check_name, 
       EXISTS(SELECT 1 FROM information_schema.columns 
              WHERE table_name = 'users' AND column_name = 'email_only') as result;

SELECT 'email_reports table exists' as check_name,
       EXISTS(SELECT 1 FROM information_schema.tables 
              WHERE table_name = 'email_reports') as result;

SELECT 'Schema fix completed successfully' as status;
