-- Migration: Change earthquake_id column from INTEGER to VARCHAR
-- This allows storing alphanumeric external IDs like "gfz2025xybv"

-- Step 1: Alter the column type
ALTER TABLE earthquakes 
ALTER COLUMN earthquake_id TYPE VARCHAR USING earthquake_id::VARCHAR;

-- Step 2: Verify the change
-- SELECT column_name, data_type FROM information_schema.columns 
-- WHERE table_name = 'earthquakes' AND column_name = 'earthquake_id';
