-- Create level ranges table
CREATE TABLE IF NOT EXISTS level_ranges (
    id SERIAL PRIMARY KEY,
    min_level INTEGER NOT NULL,
    max_level INTEGER NOT NULL,
    alias VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_min_max CHECK (min_level <= max_level),
    CONSTRAINT unique_range UNIQUE (min_level, max_level)
);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_level_ranges_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for automatic timestamp update
CREATE TRIGGER update_level_ranges_modtime
    BEFORE UPDATE ON level_ranges
    FOR EACH ROW
    EXECUTE FUNCTION update_level_ranges_timestamp();