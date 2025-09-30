-- Update users table to support email-only users
-- This script adds the email_only column to track users who only provided email for predictions

-- Add email_only column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS email_only BOOLEAN DEFAULT FALSE;

-- Update existing users to set email_only = FALSE (they are full registered users)
UPDATE users 
SET email_only = FALSE 
WHERE email_only IS NULL;

-- Allow password to be NULL for email-only users
ALTER TABLE users 
ALTER COLUMN password DROP NOT NULL;

-- Create index on email_only for faster queries
CREATE INDEX IF NOT EXISTS idx_users_email_only ON users(email_only);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Add comment to table
COMMENT ON TABLE users IS 'Users table supporting both registered users (with password) and email-only users (for predictions)';
COMMENT ON COLUMN users.email_only IS 'TRUE for users who only provided email for predictions, FALSE for fully registered users';
COMMENT ON COLUMN users.password IS 'Password hash for registered users, NULL for email-only users';

-- Refresh schema cache for PostgREST
NOTIFY pgrst, 'reload schema';

-- Display updated table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;
