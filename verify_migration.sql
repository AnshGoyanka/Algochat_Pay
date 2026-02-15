-- Verify Privacy-Enhanced Payment Migration

-- 1. Check if merchants table exists and has correct columns
SELECT 
    column_name, 
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'merchants'
ORDER BY ordinal_position;

-- 2. Check if transactions table has new columns
SELECT 
    column_name, 
    data_type
FROM information_schema.columns 
WHERE table_name = 'transactions'
AND column_name IN ('merchant_id', 'payment_ref', 'tx_id')
ORDER BY column_name;

-- 3. Count existing records
SELECT 
    'merchants' as table_name, 
    COUNT(*) as record_count 
FROM merchants
UNION ALL
SELECT 
    'transactions', 
    COUNT(*) 
FROM transactions
UNION ALL
SELECT 
    'events', 
    COUNT(*) 
FROM events
UNION ALL
SELECT 
    'funds', 
    COUNT(*) 
FROM funds;

-- 4. Check if tickets table has tx_id
SELECT 
    column_name
FROM information_schema.columns 
WHERE table_name = 'tickets'
AND column_name = 'tx_id';
