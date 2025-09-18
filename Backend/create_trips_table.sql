-- Create trips table for storing user trip information and packing lists
CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    destination VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    activities TEXT[] DEFAULT '{}',
    weather_expected VARCHAR(100),
    packing_style VARCHAR(50) DEFAULT 'minimal',
    packing_list JSONB DEFAULT '[]',
    wardrobe_matches JSONB DEFAULT '{}',
    coverage_analysis JSONB DEFAULT '{}',
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id);

-- Create index on destination for search functionality  
CREATE INDEX IF NOT EXISTS idx_trips_destination ON trips(destination);

-- Create index on dates for date range queries
CREATE INDEX IF NOT EXISTS idx_trips_dates ON trips(start_date, end_date);
