-- Privacy-Enhanced Payment System Migration
-- Adds merchant support and payment references

-- Step 1: Create merchants table
CREATE TABLE IF NOT EXISTS merchants (
    id SERIAL PRIMARY KEY,
    merchant_id VARCHAR(20) UNIQUE NOT NULL,
    merchant_name VARCHAR(200) NOT NULL,
    merchant_type VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20),
    wallet_address VARCHAR(58) NOT NULL,
    description VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    event_id INTEGER,
    fund_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for merchants
CREATE INDEX IF NOT EXISTS idx_merchants_merchant_id ON merchants(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchants_wallet ON merchants(wallet_address);
CREATE INDEX IF NOT EXISTS idx_merchants_event ON merchants(event_id);
CREATE INDEX IF NOT EXISTS idx_merchants_fund ON merchants(fund_id);

-- Step 2: Add new columns to transactions table
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS merchant_id VARCHAR(20),
ADD COLUMN IF NOT EXISTS payment_ref VARCHAR(20);

-- Create indexes for new transaction columns
CREATE INDEX IF NOT EXISTS idx_transactions_merchant_id ON transactions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_transactions_payment_ref ON transactions(payment_ref);

-- Step 3: Add tx_id column to tickets table (if not already done)
ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS tx_id VARCHAR(100);

-- Verify changes
SELECT 'Migration completed successfully!' AS status;

-- Check table structures
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'merchants'
ORDER BY ordinal_position;

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'transactions'
AND column_name IN ('merchant_id', 'payment_ref')
ORDER BY ordinal_position;
