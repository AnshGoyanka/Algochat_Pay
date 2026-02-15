-- Quick database migration for tx_id column
-- Run this in your Neon Postgres SQL Editor

-- Add tx_id column to tickets table
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS tx_id VARCHAR(100);

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'tickets';

-- Optional: View existing tickets to confirm
SELECT id, event_name, ticket_number, tx_id FROM tickets;
