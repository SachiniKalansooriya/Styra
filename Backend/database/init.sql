-- Backend/database/init.sql
-- Initialize Styra Wardrobe Database Schema

-- Users table (using SERIAL for integer IDs)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wardrobe items table
CREATE TABLE IF NOT EXISTS wardrobe_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    color VARCHAR(50),
    season VARCHAR(20) DEFAULT 'all',
    image_path VARCHAR(500),
    confidence DECIMAL(3,2),
    analysis_method VARCHAR(50),
    times_worn INTEGER DEFAULT 0,
    last_worn DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert demo user
INSERT INTO users (email, password_hash, name) VALUES 
('demo@styra.com', '$2b$12$dummy.hash.for.demo', 'Demo User')
ON CONFLICT (email) DO NOTHING;

-- Insert sample wardrobe items
INSERT INTO wardrobe_items (user_id, name, category, color, season, confidence, analysis_method) 
SELECT 
    u.id,
    item.name,
    item.category,
    item.color,
    item.season,
    item.confidence,
    item.analysis_method
FROM users u, (VALUES 
    ('Blue Denim Jeans', 'bottoms', 'Blue', 'all', 0.92, 'free_ai_analysis'),
    ('White Cotton T-Shirt', 'tops', 'White', 'summer', 0.88, 'free_ai_analysis'),
    ('Black Leather Jacket', 'outerwear', 'Black', 'winter', 0.95, 'free_ai_analysis'),
    ('Red Summer Dress', 'dresses', 'Red', 'summer', 0.90, 'free_ai_analysis'),
    ('Brown Leather Boots', 'shoes', 'Brown', 'winter', 0.87, 'free_ai_analysis')
) AS item(name, category, color, season, confidence, analysis_method)
WHERE u.email = 'demo@styra.com'
ON CONFLICT DO NOTHING;

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_user_id ON wardrobe_items(user_id);
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_category ON wardrobe_items(category);