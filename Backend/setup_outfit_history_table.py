#!/usr/bin/env python3
# setup_outfit_history_table.py
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_outfit_history_table():
    """Create the outfit_history table"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found in environment variables")
            return False
        
        print(f"Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Create outfit_history table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS outfit_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL DEFAULT 1,
            worn_date DATE NOT NULL,
            outfit_data JSONB NOT NULL,
            occasion VARCHAR(100),
            weather VARCHAR(50),
            location VARCHAR(200),
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_outfit_history_user_date 
        ON outfit_history(user_id, worn_date);
        
        CREATE INDEX IF NOT EXISTS idx_outfit_history_occasion 
        ON outfit_history(occasion);
        """
        
        print("Creating outfit_history table...")
        cursor.execute(create_table_sql)
        conn.commit()
        
        # Verify table was created
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'outfit_history'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ Outfit history table created successfully!")
            
            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'outfit_history'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"\nTable structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        else:
            print("❌ Failed to create outfit history table")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    print("=== Setting up Outfit History Table ===")
    if setup_outfit_history_table():
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed!")
