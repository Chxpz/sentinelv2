-- Treasury Sentinel Database Schema
-- Run this SQL in your Supabase SQL Editor to create the necessary tables

-- Create safes table
CREATE TABLE IF NOT EXISTS safes (
    id BIGSERIAL PRIMARY KEY,
    telegram_id TEXT NOT NULL UNIQUE,
    safe_address TEXT NOT NULL UNIQUE,
    owner1_address TEXT NOT NULL,
    owner2_address TEXT NOT NULL,
    agent_address TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    safe_address TEXT NOT NULL,
    tx_hash TEXT NOT NULL UNIQUE,
    to_address TEXT NOT NULL,
    value TEXT NOT NULL,
    data TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (safe_address) REFERENCES safes(safe_address) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_safes_telegram_id ON safes(telegram_id);
CREATE INDEX IF NOT EXISTS idx_safes_safe_address ON safes(safe_address);
CREATE INDEX IF NOT EXISTS idx_transactions_safe_address ON transactions(safe_address);
CREATE INDEX IF NOT EXISTS idx_transactions_tx_hash ON transactions(tx_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_safes_updated_at BEFORE UPDATE ON safes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (optional, for better security)
ALTER TABLE safes ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust as needed for your security requirements)
-- For now, allow all operations (you should restrict this in production)
CREATE POLICY "Enable all operations for safes" ON safes
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Enable all operations for transactions" ON transactions
    FOR ALL USING (true) WITH CHECK (true);
