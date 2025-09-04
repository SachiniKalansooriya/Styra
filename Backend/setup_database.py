import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env file")
    exit(1)

print("Connecting to Supabase database...")
engine = create_engine(DATABASE_URL)

# Test connection first
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("Connected to database successfully!")
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

# Create tables using raw SQL
print("Creating database tables...")

sql_commands = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        username VARCHAR(50) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        full_name VARCHAR(100),
        is_active BOOLEAN NOT NULL DEFAULT true,
        preferences TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS wardrobe_items (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        color VARCHAR(30) NOT NULL,
        brand VARCHAR(100),
        size VARCHAR(20),
        season VARCHAR(20) DEFAULT 'All',
        formality_level VARCHAR(30) DEFAULT 'Casual',
        image_url VARCHAR(500),
        times_worn INTEGER NOT NULL DEFAULT 0,
        last_worn TIMESTAMP WITH TIME ZONE,
        is_available BOOLEAN NOT NULL DEFAULT true,
        is_favorite BOOLEAN NOT NULL DEFAULT false,
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE,
        owner_id UUID REFERENCES users(id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_wardrobe_items_category ON wardrobe_items(category);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_wardrobe_items_owner ON wardrobe_items(owner_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_wardrobe_items_available ON wardrobe_items(is_available);
    """
]

try:
    with engine.connect() as conn:
        for command in sql_commands:
            conn.execute(text(command))
            conn.commit()
    
    print("Tables created successfully!")
    print("\nCreated tables:")
    print("- users (id, email, username, hashed_password, full_name, is_active, preferences, created_at, updated_at)")
    print("- wardrobe_items (id, name, category, color, brand, size, season, formality_level, image_url, times_worn, last_worn, is_available, is_favorite, notes, created_at, updated_at, owner_id)")
    print("\nCreated indexes for better performance")
    print("Your database is ready!")
    
except Exception as e:
    print(f"Error creating tables: {e}")